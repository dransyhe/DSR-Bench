from sklearn import datasets
import numpy as np

def gen_circle(n_samples, random_state):
    X, y = datasets.make_circles(
        n_samples=n_samples, factor=0.5, noise=0.05, random_state = random_state
    )
    X = np.round((X * 100 + 100)/2).astype(int)
    return X

def gen_moons(n_samples, random_state):
    X, y = datasets.make_moons(
        n_samples=n_samples, noise=0.05, random_state = random_state
    )
    X = np.round((X * 100 + 100)/2).astype(int)
    return X

def gen_blobs(n_samples, random_state):
    X, y = datasets.make_blobs(
        n_samples=n_samples, random_state=random_state
    )
    X = np.round(X * 100 /10 + 50).astype(int)
    return X

if __name__ == "__main__":
    n_samples = 10
    X = gen_circle(n_samples)
    print(X)
    # print(y)