from _data import load_prices

from finance.analytics import returns
from finance.data import close_matrix
from finance.models import cluster_assets, pca


def main():
    changes = returns(close_matrix(load_prices(("AAPL", "MSFT", "NVDA", "JPM", "SPY")))).dropna()
    print(cluster_assets(changes, clusters=2, components=2).to_string())
    print(pca(changes).explained_variance.round(3).to_string())


if __name__ == "__main__":
    main()
