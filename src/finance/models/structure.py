from dataclasses import dataclass

import numpy as np
import pandas as pd

from finance._validation import frame, window_size


@dataclass(frozen=True)
class PCAResult:
    loadings: pd.DataFrame
    scores: pd.DataFrame
    explained_variance: pd.Series


def pca(returns: pd.DataFrame, components: int = 2) -> PCAResult:
    """Descriptive cross-asset PCA of standardized returns; not an out-of-sample portfolio."""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    returns = frame(returns)
    window_size(components)
    if components > min(returns.shape) or (returns.std() == 0).any():
        raise ValueError("invalid component count or constant asset")
    scaled = StandardScaler().fit_transform(returns)
    fitted = PCA(n_components=components).fit(scaled)
    names = [f"pc{i + 1}" for i in range(components)]
    return PCAResult(
        pd.DataFrame(fitted.components_.T, index=returns.columns, columns=names),
        pd.DataFrame(fitted.transform(scaled), index=returns.index, columns=names),
        pd.Series(fitted.explained_variance_ratio_, index=names),
    )


def cluster_assets(
    returns: pd.DataFrame,
    clusters: int = 3,
    *,
    components: int | None = None,
    method: str = "kmeans",
    seed: int = 0,
) -> pd.Series:
    """Cluster assets (rows), not dates, using standardized return paths or PCA loadings."""
    from sklearn.cluster import KMeans
    from sklearn.mixture import GaussianMixture
    from sklearn.preprocessing import StandardScaler

    returns = frame(returns)
    window_size(clusters)
    if clusters > returns.shape[1] or (returns.std() == 0).any():
        raise ValueError("too many clusters or constant asset")
    features = (
        pca(returns, components).loadings
        if components is not None
        else pd.DataFrame(StandardScaler().fit_transform(returns).T, index=returns.columns)
    )
    if method == "kmeans":
        labels = KMeans(n_clusters=clusters, n_init=20, random_state=seed).fit_predict(features)
    elif method == "mixture":
        labels = GaussianMixture(
            n_components=clusters, random_state=seed, reg_covar=1e-5
        ).fit_predict(features)
    else:
        raise ValueError("method must be kmeans or mixture")
    return pd.Series(labels, index=returns.columns, name="cluster")


def cluster_features(features: pd.DataFrame, clusters: int = 3, seed: int = 0) -> pd.Series:
    """Cluster one row per asset of supplied technical/fundamental features."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    features = frame(features)
    window_size(clusters)
    if clusters > len(features):
        raise ValueError("more clusters than assets")
    labels = KMeans(n_clusters=clusters, n_init=20, random_state=seed).fit_predict(
        StandardScaler().fit_transform(features)
    )
    return pd.Series(labels, index=features.index, name="cluster")


def partial_correlations(returns: pd.DataFrame, alpha: float = 0.1) -> pd.DataFrame:
    """Descriptive regularized conditional dependence; fixed alpha, no predictive claim."""
    from sklearn.covariance import GraphicalLasso
    from sklearn.preprocessing import StandardScaler

    returns = frame(returns)
    if not np.isfinite(alpha) or alpha <= 0 or (returns.std() == 0).any():
        raise ValueError("positive alpha and nonconstant assets required")
    fitted = GraphicalLasso(alpha=alpha, max_iter=500).fit(StandardScaler().fit_transform(returns))
    if fitted.n_iter_ >= 500:
        raise ValueError("graphical lasso did not converge")
    precision = fitted.precision_
    scale = np.sqrt(np.diag(precision))
    result = -precision / np.outer(scale, scale)
    np.fill_diagonal(result, 1)
    return pd.DataFrame(result, index=returns.columns, columns=returns.columns)


def anomaly_scores(training: pd.DataFrame, observations: pd.DataFrame, seed: int = 0) -> pd.Series:
    """Isolation Forest novelty scores fitted only on earlier observations; lower is more unusual."""
    from sklearn.ensemble import IsolationForest
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    training, observations = frame(training), frame(observations)
    if (
        not training.columns.equals(observations.columns)
        or training.index[-1] >= observations.index[0]
    ):
        raise ValueError("require matching features and training strictly before observations")
    model = make_pipeline(
        StandardScaler(), IsolationForest(random_state=seed, contamination="auto")
    )
    model.fit(training)
    return pd.Series(
        model.decision_function(observations), index=observations.index, name="anomaly_score"
    )


def cointegration_pairs(prices: pd.DataFrame) -> pd.DataFrame:
    """Engle-Granger tests on supplied training prices; Holm-adjusted p-values across pairs."""
    from statsmodels.stats.multitest import multipletests
    from statsmodels.tsa.stattools import coint

    prices = frame(prices, positive=True)
    if len(prices) < 40 or prices.shape[1] < 2:
        raise ValueError("provide at least two assets and 40 training observations")
    rows = []
    for i, first in enumerate(prices):
        for second in prices.columns[i + 1 :]:
            statistic, probability, _ = coint(np.log(prices[first]), np.log(prices[second]))
            rows.append(
                {"first": first, "second": second, "statistic": statistic, "p_value": probability}
            )
    result = pd.DataFrame(rows)
    result["adjusted_p_value"] = multipletests(result.p_value, method="holm")[1]
    return result.sort_values("adjusted_p_value", ignore_index=True)
