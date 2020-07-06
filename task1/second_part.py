from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

from first_task import BD_API_influx


def decor(bd: BD_API_influx):
    def animate(_):
        wr = bd.get_points()
        if len(wr) == 0:
            return
        plt.cla()
        pts = {}
        time_pts = {}
        for pt_it in wr:
            time = int(pt_it.pop("time", 0))
            for var_it in pt_it:
                is_var = pts.get(var_it, None)
                if is_var is None:
                    pts[var_it] = []
                    time_pts[var_it] = []
                pts[var_it].append(pt_it[var_it])
                time_pts[var_it].append(time)
        for nm_vars in pts:
            plt.plot(time_pts[nm_vars], pts[nm_vars], label=nm_vars)
        plt.tight_layout()
        plt.legend(loc='lower left')
    return animate


if __name__ == "__main__":
    bd = BD_API_influx("localhost", "eldata", "izmerenie1")
    ani = FuncAnimation(plt.gcf(), decor(bd), interval=1000)
    plt.tight_layout()
    plt.show()
