plot tanks

######## PLOTS ##########
def plot_tanks(model):
    l1 = []
    l2 = []
    l3 = []
    l4 = []
    l5 = []

    F1 = []
    F2 = []
    F3 = []
    F4 = []
    F5 = []
    F0 = []
    w1 = []
    w2 = []
    w3 = []
    w4 = []
    w5 = []
    w0 = []

    y_1 = []
    y2_1 = []
    sp_1 = []
    sn_1 = []
    y_2 = []
    y2_2 = []
    sp_2 = []
    sn_2 = []
    y_3 = []
    y2_3 = []
    sp_3 = []
    sn_3 = []
    y_4 = []
    y2_4 = []
    y_5 = []
    y2_5 = []

    for t in m.t:

        l1.append(m.L[1,t].value)
        l2.append(m.L[2,t].value)
        l3.append(m.L[3,t].value)
        F0.append(m.F0[t].value)
        F1.append(m.F[1,t].value)
        F2.append(m.F[2,t].value)
        F3.append(m.F[3,t].value)
        w0.append(m.w0[t].value)
        w1.append(m.w[1,t].value)
        w2.append(m.w[2,t].value)
        w3.append(m.w[3,t].value)

        y_1.append(m.y[1,t].value)
        y2_1.append(m.y2[1,t].value)
        sp_1.append(m.sp[1,t].value)
        sn_1.append(m.sn[1,t].value)
        y_2.append(m.y[2,t].value)
        y2_2.append(m.y2[2,t].value)
        sp_2.append(m.sp[2,t].value)
        sn_2.append(m.sn[2,t].value)
        y_3.append(m.y[3,t].value)
        y2_3.append(m.y2[3,t].value)
        sp_3.append(m.sp[3,t].value)
        sn_3.append(m.sn[3,t].value)
        if Ntank > 3:
            y_4.append(m.y[4,t].value)
            y2_4.append(m.y2[4,t].value)
            y_5.append(m.y[5,t].value)
            y2_5.append(m.y2[5,t].value)
            l4.append(m.L[4,t].value)
            l5.append(m.L[5,t].value)
            w4.append(m.w[4,t].value)
            w5.append(m.w[5,t].value)
            F4.append(m.F[4,t].value)
            F5.append(m.F[5,t].value)

    plt.subplot(221)

    plt.plot(m.t, l1, label='l1')
    plt.plot(m.t, l2, label='l2')
    plt.plot(m.t, l3, label='l3')
    if Ntank > 3:
        plt.plot(m.t, l4, label='l4')
        plt.plot(m.t, l5, label='l5')
    plt.legend()
    plt.subplot(222)
    plt.plot(m.t, F0, label='F0')
    plt.plot(m.t, F1, label='F1')
    plt.plot(m.t, F2, label='F2')
    plt.plot(m.t, F3, label='F3')
    if Ntank > 3:
        plt.plot(m.t, F4, label='F4')
        plt.plot(m.t, F5, label='F5')
    plt.legend()
    plt.subplot(223)
    plt.plot(m.t, w0, label='w0')
    plt.plot(m.t, w1, label='w1')
    plt.plot(m.t, w2, label='w2')
    plt.plot(m.t, w3, label='w3')
    if Ntank > 3:
        plt.plot(m.t, w4, label='w4')
        plt.plot(m.t, w5, label='w5')
    plt.legend()
    plt.subplot(224)
    plt.plot(m.t, y2_1, label='y2_1')
    # plt.plot(m.t, sp_1, label='sp_1')
    plt.plot(m.t, y_1, label='y_1')
    # plt.plot(m.t, sn_1, label='sn_1')
    plt.plot(m.t, y2_2, label='y2_2')
    # plt.plot(m.t, sp_2, label='sp_2')
    plt.plot(m.t, y_2, label='y_2')
    # plt.plot(m.t, sn_2, label='sn_2')
    plt.plot(m.t, y2_3, label='y2_3')
    # plt.plot(m.t, sp_3, label='sp_3')
    plt.plot(m.t, y_3, label='y_3')
    # plt.plot(m.t, sn_3, label='sn_3')
    if Ntank > 3:
        plt.plot(m.t, y2_4, label='y2_4')
        plt.plot(m.t, y_4, label='y_4')
        plt.plot(m.t, y2_5, label='y2_5')
        plt.plot(m.t, y_5, label='y_5')
    plt.legend()

    plt.ion()
    plt.show()
