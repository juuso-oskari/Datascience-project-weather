import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import collections
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sn

def knn_optimize(x_train, x_test, y_train, y_test, show_plot=False):
    """
    Finds the optimal minimum number of neighbors to use for the KNN classifier.
    :param show_plot: bool, when True shows the plot of number of neighbors vs error
            Default: False
    :return: the number of neighbors (int)
    """

    error = []

    # Calculating error for K values between 1 and 40
    for i in range(1, 40):
        knn = KNeighborsClassifier(n_neighbors=i)
        knn.fit(x_train, y_train)
        pred_i = knn.predict(x_test)
        error.append(np.mean(pred_i != y_test))

    m = min(error)
    min_ind = error.index(m)

    if show_plot:
        plt.figure(figsize=(12, 6))
        plt.plot(range(1, 40), error, color='red', linestyle='dashed', marker='o',
                 markerfacecolor='blue', markersize=10)
        plt.title('Error Rate K Value')
        plt.xlabel('K Value')
        plt.ylabel('Mean Error')
        plt.show()

    return min_ind + 1


if __name__ == "__main__":

    X_train = pd.read_csv('../res/weather_data_train.csv', index_col='datetime',
                          sep=';', decimal=',', infer_datetime_format=True)

    Y_train = pd.read_csv('../res/weather_data_train_labels.csv', index_col='datetime',
                          sep=';', decimal=',', infer_datetime_format=True)

    X_test = pd.read_csv('../res/weather_data_test.csv', index_col='datetime',
                         sep=';', decimal=',', infer_datetime_format=True)

    Y_test = pd.read_csv('../res/weather_data_test_labels.csv', index_col='datetime',
                         sep=';', decimal=',', infer_datetime_format=True)

    # lets standardize our data first
    X_std = StandardScaler().fit_transform(X_train)

    X_test_std = StandardScaler().fit_transform(X_test)

    pca_func = PCA(n_components=8)
    PCA_cmps = pca_func.fit_transform(X_std)
    test_PCA_cmps = pca_func.fit_transform(X_test_std)

    n = knn_optimize(PCA_cmps, test_PCA_cmps, Y_train['OBSERVED'], Y_test['OBSERVED'], show_plot=True)

    # We find that k=31 produces minimal error
    knn = KNeighborsClassifier(n_neighbors=n)
    knn.fit(PCA_cmps, Y_train['OBSERVED'])
    pred_i = knn.predict(test_PCA_cmps)

    final_df = pd.DataFrame(data={'PCA_1': PCA_cmps[:, 0], 'PCA_2': PCA_cmps[:, 1], 'PCA_3': PCA_cmps[:, 2],
                                  'OBSERVED': Y_train['OBSERVED']})
    pred_df = pd.DataFrame(data={'PCA_1': test_PCA_cmps[:, 0], 'PCA_2': test_PCA_cmps[:, 1], 'PCA_3': test_PCA_cmps[:, 2],
                                 'PREDICTED': pred_i, 'OBSERVED': Y_test['OBSERVED']})

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    ax.set_xlabel('Principal Component 1', fontsize=15)
    ax.set_ylabel('Principal Component 2', fontsize=15)
    ax.set_title('2 component PCA', fontsize=15)

    for i, row in final_df.iterrows():
        if row['OBSERVED'] == 1:
            ax.scatter(row['PCA_1'], row['PCA_2'], c='r', s=5, label="1")
        else:
            ax.scatter(row['PCA_1'], row['PCA_2'], c='b', s=5, label="0")

    confused_dry = 0
    for i, row in pred_df.iterrows():
        if row['OBSERVED'] != row['PREDICTED']:
            if row['OBSERVED'] == 1:
                confused_dry += 1
            ax.scatter(row['PCA_1'], row['PCA_2'], c='black', s=10, label="misclassified")
        else:
            if row['PREDICTED'] == 1:
                ax.scatter(row['PCA_1'], row['PCA_2'], c='y', s=5, label="correct prediction 1")  # yellow marks the days classified to be dry by knn
            else:
                ax.scatter(row['PCA_1'], row['PCA_2'], c='g', s=5, label="correct prediction 0")  # green marks the days classified to be not dry by knn
    print(confused_dry)
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Classifications')
    plt.show()
    conf_matrix = confusion_matrix(Y_test['OBSERVED'], pred_df['PREDICTED'])
    print(conf_matrix)
    df_cm = pd.DataFrame(conf_matrix, index=[i for i in "10"],
                         columns=[i for i in "10"])
    plt.figure()
    sn.heatmap(df_cm)
    plt.xlabel('Predictions')
    plt.ylabel('Observations')
    plt.show()