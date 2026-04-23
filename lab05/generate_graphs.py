import matplotlib.pyplot as plt

# все в Мбит
F = 15 * 1000
u_s = 30
d_i = 2 
u_values = [0.3, 0.7, 2]
N_values = [i for i in range(10, 991)]
for u in u_values:
    for n in [10, 100, 1000]:
        plt.scatter(n, max(n * F / u_s, F / d_i), color='blue', zorder=3)
        plt.scatter(n, max(F / u_s, F / d_i, n * F / (u_s + n * u)), color='orange', zorder=3)
    d_values_cs = [max(N * F / u_s, F / d_i) for N in N_values]
    d_values_p2p = [max(F / u_s, F / d_i, N * F / (u_s + N * u)) for N in N_values]
    plt.title(f"u = {u} Мбит/с")
    plt.plot(N_values, d_values_cs, label="Client-Server")
    plt.plot(N_values, d_values_p2p, label="P2P")
    plt.xlabel("N")
    plt.ylabel("Time (s)")
    plt.yscale('log')
    plt.legend()
    plt.savefig(f"img/graph_u{u}.png")
    plt.clf()
