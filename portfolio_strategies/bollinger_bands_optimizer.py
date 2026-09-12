import warnings
# --- 경고 무시 설정: 깔끔한 출력을 위해 모든 경고를 무시합니다. ---
warnings.filterwarnings("ignore")
# --------------------

import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
from itertools import product

# Matplotlib 한글 폰트 설정
try:
    plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 기본 폰트
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
except:
    print("\n[Matplotlib 폰트 경고] 한글 폰트를 찾을 수 없습니다. 그래프의 한글 텍스트가 깨질 수 있습니다.")
    plt.rcParams['font.family'] = 'DejaVu Sans' 

# --- 설정 상수 (Bollinger Bands 기준) ---
TICKER = 'OKLO' 
START_DATE = '2024-05-09'
END_DATE = None
# --- 최적화 파라미터 범위 정의 ---
N_PERIODS = range(10, 31, 5) # N (기간): 10, 15, 20, 25, 30
K_MULTIPLIERS = [1.5, 2.0, 2.5, 3.0] # K (표준편차 배수): 1.5, 2.0, 2.5, 3.0


# --- 1. 데이터 다운로드 및 준비 (CLOSE, HIGH, LOW 필요) ---
def download_data():
    """Bollinger Bands 계산에 필요한 'CLOSE', 'HIGH', 'LOW' 컬럼을 다운로드하고 아웃라이어를 제거합니다."""
    print(f"--- 1. {TICKER} 주식 데이터 다운로드 시작 (기간: {START_DATE} ~ {END_DATE if END_DATE else '최신일'}) ---")
    try:
        data = yf.download(TICKER, start=START_DATE, end=END_DATE)
        
        if data.empty:
            print("데이터를 다운로드했으나, 데이터프레임이 비어있습니다. 티커를 확인해 주세요.")
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(-1)
        
        data.columns = [col.upper().strip() for col in data.columns]
        
        # OKLO 비표준 컬럼 이슈 처리 (Adjusted Close를 최종 거래 가격으로 사용)
        if len(data.columns) >= 5 and all(col == TICKER.upper() for col in data.columns.tolist()):
            standard_names = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'ADJ CLOSE', 'VOLUME']
            data.columns = standard_names[:len(data.columns)]
            print(f"\n[데이터 클렌징 알림]: 비표준 컬럼 이름 ({TICKER})이 감지되어, 표준 순서로 강제 재정의되었습니다.")

        data['CLOSE'] = data.get('ADJ CLOSE', data.get('CLOSE'))
        
        required_cols = ['CLOSE', 'HIGH', 'LOW']
        
        if not all(col in data.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in data.columns]
            print(f"다운로드된 데이터에 {required_cols} 중 부족한 컬럼이 있습니다. (누락: {missing_cols})")
            return pd.DataFrame()
            
        data_cols = data[required_cols].copy()
        
        for col in required_cols:
             if data_cols[col].dtype != np.float64:
                 try:
                    data_cols[col] = data_cols[col].astype(float)
                 except ValueError:
                    print(f"데이터 경고: '{col}' 컬럼을 float으로 변환할 수 없습니다. 데이터를 건너뜁니다.")
                    return pd.DataFrame()

        # 아웃라이어 제거
        quantile_999 = data_cols['CLOSE'].quantile(0.999)
        initial_count = len(data_cols)
        data_cols = data_cols[data_cols['CLOSE'] <= quantile_999]
        removed_count = initial_count - len(data_cols)

        if removed_count > 0:
            print(f"\n[데이터 클렌징 알림]: 극단적인 아웃라이어 {removed_count}개를 제거했습니다.")
        
        print(f"다운로드 완료. 총 데이터 개수: {data_cols.shape[0]}일")
        return data_cols
        
    except Exception as e:
        print(f"치명적 오류: 데이터 다운로드 중 오류 발생: {e}")
        return pd.DataFrame()


# --- 2. 백테스팅 로직 (수익률과 거래 횟수 반환) ---
def backtest_strategy(data, n_period, k_multiplier):
    """
    Bollinger Bands 역추세(밴드 재진입) 전략을 백테스팅하고 
    누적 수익률(복리)과 거래 횟수를 반환합니다.
    """
    if data.empty:
        return 0, 0

    df = data.copy()
    
    # Bollinger Bands 계산
    df['Upper'], df['Middle'], df['Lower'] = ta.BBANDS(
        df['CLOSE'].values,
        timeperiod=n_period,
        nbdevup=k_multiplier,
        nbdevdn=k_multiplier,
        matype=0  # Simple Moving Average
    )
    
    df.dropna(inplace=True)
    if df.empty:
        return 0, 0
    
    # BB 역추세(밴드 재진입) 매매 신호 로직
    # 매수: 종가가 하한선 아래 -> 오늘 하한선 위로 진입
    df['Buy_Signal'] = (df['CLOSE'].shift(1) < df['Lower'].shift(1)) & (df['CLOSE'] > df['Lower'])
    # 매도: 종가가 상한선 위 -> 오늘 상한선 아래로 진입 (포지션 정리)
    df['Sell_Signal'] = (df['CLOSE'].shift(1) > df['Upper'].shift(1)) & (df['CLOSE'] < df['Upper'])
    
    # 포지션 관리 및 수익률 계산
    is_holding = False
    buy_price = 0
    trades = [] # 실현된 거래의 수익률을 저장
    
    for i in range(len(df)):
        current_close = df['CLOSE'].iloc[i]
        
        # 매수 신호 발생 및 현재 포지션이 없는 경우
        if df['Buy_Signal'].iloc[i] and not is_holding:
            buy_price = current_close
            is_holding = True

        # 매도 신호 발생 및 현재 포지션이 있는 경우
        elif df['Sell_Signal'].iloc[i] and is_holding:
            profit = (current_close - buy_price) / buy_price
            trades.append(profit)
            is_holding = False

    # 마지막 날까지 포지션을 정리하지 못하고 종료된 경우, 마지막 종가로 정리
    if is_holding:
        final_price = df['CLOSE'].iloc[-1]
        profit = (final_price - buy_price) / buy_price
        trades.append(profit)

    if not trades:
        return 0, 0
        
    cumulative_profit = (np.prod([(1 + t) for t in trades]) - 1) * 100
    total_trades = len(trades) # 매수/매도 한 쌍의 거래 횟수
    
    return cumulative_profit, total_trades

# --- 4. 그래프 생성을 위한 일별 수익률 계산 및 플로팅 함수 ---
def calculate_daily_strategy_cumulative_returns(data, n_period, k_multiplier):
    """최적화된 파라미터로 전략의 일별 누적 수익률을 계산하여 반환합니다."""
    df = data.copy()
    
    # Bollinger Bands 계산
    df['Upper'], df['Middle'], df['Lower'] = ta.BBANDS(
        df['CLOSE'].values,
        timeperiod=n_period,
        nbdevup=k_multiplier,
        nbdevdn=k_multiplier,
        matype=0 
    )
    df.dropna(inplace=True)
    if df.empty:
        return pd.Series(1.0, index=data.index)
        
    # BB 역추세 포지션 생성 로직 (일별 누적 수익률 계산을 위해 포지션 유지 여부를 기록)
    df['Buy_Signal'] = (df['CLOSE'].shift(1) < df['Lower'].shift(1)) & (df['CLOSE'] > df['Lower'])
    df['Sell_Signal'] = (df['CLOSE'].shift(1) > df['Upper'].shift(1)) & (df['CLOSE'] < df['Upper'])
    
    df['Position'] = 0 # 1: 매수 포지션, 0: 포지션 없음
    is_holding = 0
    
    for i in range(len(df)):
        if df['Buy_Signal'].iloc[i]:
            is_holding = 1 # 매수 신호 발생 -> 포지션 진입
        elif df['Sell_Signal'].iloc[i]:
            is_holding = 0 # 매도 신호 발생 -> 포지션 종료
        
        df.loc[df.index[i], 'Position'] = is_holding

    df.loc[:, 'Position'] = df['Position'].shift(1).fillna(0)
    
    # 일별 수익률 계산: 전일 대비 수익률 * 전일 포지션
    df.loc[:, 'Strategy_Daily_Return'] = df['CLOSE'].pct_change() * df['Position']
    df.loc[:, 'Strategy_Daily_Return'].fillna(0, inplace=True)

    # 누적 수익률 (Cumulative Product)
    df.loc[:, 'Strategy_Cumulative'] = (1 + df['Strategy_Daily_Return']).cumprod()
    df.loc[:, 'Strategy_Cumulative'].iloc[0] = 1.0 # 첫 날은 1.0으로 시작
    
    # Buy & Hold 수익률 계산
    df.loc[:, 'Buy_Hold_Daily_Return'] = df['CLOSE'].pct_change()
    df.loc[:, 'Buy_Hold_Daily_Return'].fillna(0, inplace=True)
    df.loc[:, 'Buy_Hold_Cumulative'] = (1 + df['Buy_Hold_Daily_Return']).cumprod()
    df.loc[:, 'Buy_Hold_Cumulative'].iloc[0] = 1.0

    return df[['Strategy_Cumulative', 'Buy_Hold_Cumulative']]

def plot_optimization_results(ohlc_data, all_results, best_params):
    """최적화 결과 및 최고 전략의 누적 수익률 그래프를 생성하고 화면에 표시합니다."""
    
    results_df = pd.DataFrame(all_results)
    
    # 최적 파라미터 (N, K, Trades) 추출
    best_n, best_k, best_trades = best_params 
    
    # 두 개의 서브플롯 생성
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    # -----------------------------------
    # Plot 1: 파라미터 조합 vs. 수익률 (Heatmap/Scatter)
    # -----------------------------------
    ax1 = axes[0]
    
    scatter = ax1.scatter(
        results_df['N_Period'], 
        results_df['K_Multiplier'], 
        c=results_df['Profit'], 
        cmap='viridis', 
        s=400, # 마커 크기
        alpha=0.8,
        edgecolor='k'
    )
    
    # 최적 파라미터 강조
    ax1.scatter(best_n, best_k, s=800, color='red', marker='*', label=f'최적 파라미터 N={best_n}, K={best_k}', zorder=5)

    ax1.set_title(f'Bollinger Bands 파라미터별 누적 수익률 분포 (역추세 전략)', fontsize=14, pad=15)
    ax1.set_xlabel('N (기간)', fontsize=12)
    ax1.set_ylabel('K (표준편차 배수)', fontsize=12)
    ax1.set_xticks(list(N_PERIODS))
    ax1.set_yticks(K_MULTIPLIERS)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # 컬러바 추가
    cbar = fig.colorbar(scatter, ax=ax1, orientation='vertical', pad=0.05)
    cbar.set_label('누적 수익률 (%)', rotation=270, labelpad=15)
    ax1.legend()


    # -----------------------------------
    # Plot 2: 누적 수익률 비교 (Equity Curve)
    # -----------------------------------
    
    # 최적 전략의 일별 누적 수익률 계산
    cumulative_returns_df = calculate_daily_strategy_cumulative_returns(ohlc_data, best_n, best_k)
    
    ax2 = axes[1]
    
    # 최적 전략 수익률
    ax2.plot(cumulative_returns_df.index, cumulative_returns_df['Strategy_Cumulative'], 
              label=f'최적 BB 전략 (N={best_n}, K={best_k})', color='darkblue', linewidth=2)
    
    # Buy & Hold 수익률
    ax2.plot(cumulative_returns_df.index, cumulative_returns_df['Buy_Hold_Cumulative'], 
              label='Buy & Hold', color='red', linestyle='--', linewidth=2)

    ax2.set_title(f'최적 BB 전략 vs. Buy & Hold 누적 수익률 비교 ({TICKER})', fontsize=14, pad=15)
    ax2.set_xlabel('날짜', fontsize=12)
    ax2.set_ylabel('누적 수익률 (기준일 100%)', fontsize=12)
    
    # Y축 포맷팅 (기준 1.0 = 100%)
    from matplotlib.ticker import FuncFormatter
    formatter = FuncFormatter(lambda y, pos: f"{y*100:.0f}%")
    ax2.yaxis.set_major_formatter(formatter)

    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    
    # 파일로 저장하는 대신, 바로 화면에 표시 (plt.show() 사용)
    print("\n--- 4. 시각화 결과 표시 ---")
    print("[시각화 알림] 최적화 결과 그래프를 화면에 표시합니다. 창을 닫으면 다음 단계로 진행됩니다.")
    plt.show()


# --- 3. 최적화 실행 (모든 결과 저장) ---
def optimize_bollinger_bands_parameters(data):
    """
    주어진 파라미터 범위 내에서 Bollinger Bands 조합을 테스트하고 모든 결과를 반환합니다.
    """
    if data.empty:
        # 수익률, 거래횟수, Buy&Hold, 최적 파라미터
        return [], 0, 0, (0, 0, 0)
        
    all_results = []
    best_profit = -float('inf')
    best_params = (0, 0, 0) # N, K, Trades
    
    total_combinations = len(N_PERIODS) * len(K_MULTIPLIERS)

    print(f"\n--- 2. Bollinger Bands 파라미터 최적화 시작 ({total_combinations}개 조합 테스트) ---")
    
    # 모든 N과 K 조합을 생성
    for n_period, k_multiplier in product(N_PERIODS, K_MULTIPLIERS):
        # 수익률과 거래 횟수를 동시에 반환받음
        profit, trade_count = backtest_strategy(data, n_period, k_multiplier)
        
        all_results.append({
            'N_Period': n_period,
            'K_Multiplier': k_multiplier,
            'Profit': profit,
            'Trades': trade_count # 거래 횟수 저장
        })
        
        if profit > best_profit:
            best_profit = profit
            # 최적 파라미터와 거래 횟수를 튜플로 저장
            best_params = (n_period, k_multiplier, trade_count)
            
    # Buy & Hold 수익률 계산
    if not data.empty:
        buy_and_hold_return = ((data['CLOSE'].iloc[-1] - data['CLOSE'].iloc[0]) / data['CLOSE'].iloc[0] * 100).item()
    else:
        buy_and_hold_return = 0

    return all_results, best_profit, buy_and_hold_return, best_params


# --- 메인 실행 블록 ---
if __name__ == "__main__":
    
    ohlc_data = download_data()
    
    if not ohlc_data.empty:
        # 최적화 실행
        all_results, best_profit, buy_and_hold_return, best_params = optimize_bollinger_bands_parameters(ohlc_data)

        # 결과 정렬 (수익률 내림차순)
        sorted_results = sorted(all_results, key=lambda x: x['Profit'], reverse=True)
        
        # 상위 10개 결과
        top_10 = sorted_results[:10]
        
        # 하위 10개 결과 추출 (수익률 오름차순)
        worst_sorted = sorted(all_results, key=lambda x: x['Profit'])
        worst_10 = worst_sorted[:10]
        
        # 최적 파라미터 언패킹
        best_n, best_k, best_trades = best_params

        # 결과 출력 (Markdown 형식으로 보고서 생성, LaTeX 적용)
        print("\n--- 3. Bollinger Bands 최적화 최종 결과 보고 ---")
        
        # LaTeX 포맷팅
        print(f"| 키: $\\text{{N Period}}$ (기간), $\\text{{K Multiplier}}$ (배수), $\\text{{Profit}}$ (수익률), $\\text{{Trades}}$ (거래 횟수) |")
        print("-" * 85)
        print(f"**종목:** {TICKER}")
        print(f"**기간:** {START_DATE} ~ {ohlc_data.index[-1].strftime('%Y-%m-%d')}")
        print(f"**검증 조합 수:** {len(all_results)}개")
        
        # 테스트 범위 LaTeX 포맷팅
        latex_part_n = r"\{" + str(list(N_PERIODS)[0]) + r", \dots, " + str(list(N_PERIODS)[-1]) + r"\}"
        latex_part_k = r"\{" + str(list(K_MULTIPLIERS)[0]) + r", \dots, " + str(list(K_MULTIPLIERS)[-1]) + r"\}"
        print(f"**테스트 범위:** $\\text{{N Period}} \in {latex_part_n}$, $\\text{{K Multiplier}} \in {latex_part_k}$")
        print("-" * 85)
        
        print(f"**💰 동일 기간 Buy & Hold 수익률:** $\mathbf{{ {buy_and_hold_return:.2f}\\% }}$")
        print(f"**🏆 최적 BB 전략 누적 수익률:** $\mathbf{{ {best_profit:.2f}\\% }}$")
        print(f"**최적 파라미터 (N/K):** $\mathbf{{ {best_n} / {best_k} }}$")
        print(f"**최적 전략 거래 횟수:** $\mathbf{{ {best_trades} }}$회")
        print("-" * 85)

        # --- 상위 10개 출력 ---
        print("\n## 상위 최적 파라미터 조합 (Top Results)")
        print("| 순위 | N Period | K Multiplier | 누적 수익률 (%) | 거래 횟수 |")
        print("|:----:|:--------:|:------------:|:--------------:|:--------:|")
        for i, res in enumerate(top_10):
            print(f"| {i+1} | {res['N_Period']:^8} | {res['K_Multiplier']:^12} | {res['Profit']:.2f}% | {res['Trades']:^7} |")

        # --- 하위 10개 출력 ---
        print("\n## 하위 최악 파라미터 조합 (Worst Results)")
        print("| 순위 | N Period | K Multiplier | 누적 수익률 (%) | 거래 횟수 |")
        print("|:----:|:--------:|:------------:|:--------------:|:--------:|")
        for i, res in enumerate(worst_10):
            print(f"| {i+1} | {res['N_Period']:^8} | {res['K_Multiplier']:^12} | {res['Profit']:.2f}% | {res['Trades']:^7} |")
            
        # --- 그래프 생성 및 표시 ---
        plot_optimization_results(ohlc_data, all_results, best_params)
        
    else:
        print("\n데이터 문제로 인해 최적화를 실행할 수 없습니다. 티커를 확인해 주세요.")
