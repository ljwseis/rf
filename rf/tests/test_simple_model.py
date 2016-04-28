"""
Tests for simple_model module.
"""
import numpy as np
from obspy.geodetics import degrees2kilometers
from obspy.taup import TauPyModel
from rf import read_rf
from rf.simple_model import load_model
import unittest


class SimpleModelTestCase(unittest.TestCase):

    def setUp(self):
        self.model = load_model()

    def test_ppoint_vs_XY(self):
        """
        import rf._xy
        print(rf._xy.pspier.__doc__)
        print(rf._xy.pspier(100, 0, 0, 6.4, 0))
        print(rf._xy.sppier(100, 0, 0, 6.4, 0))

        Output:
            Wrapper for ``pspier``.

            Parameters
            ----------
            depth : input float
            slat : input rank-1 array('d') with bounds (n)
            slon : input rank-1 array('d') with bounds (n)
            slow : input rank-1 array('d') with bounds (n)
            azim : input rank-1 array('d') with bounds (n)

            Other Parameters
            ----------------
            n : input int, optional
                Default: len(slat)

            Returns
            -------
            rpier : rank-1 array('d') with bounds (n)
            plat : rank-1 array('d') with bounds (n)
            plon : rank-1 array('d') with bounds (n)

            (array([ 25.04094341]), array([ 0.22518834]), array([ 0.]))
            (array([ 47.99740106]), array([ 0.43163133]), array([ 0.]))
        """
        r_ps_xy = 25.0
        lat_ps_xy = 0.225
        r_sp_xy = 48.0
        lat_sp_xy = 0.432
        r_ps = self.model.ppoint_distance(100, 6.4, phase='S')
        r_sp = self.model.ppoint_distance(100, 6.4, phase='P')
        self.assertLess(abs(r_ps-r_ps_xy)/r_ps_xy, 0.05)
        self.assertLess(abs(r_sp-r_sp_xy)/r_sp_xy, 0.05)
        stats = {'station_latitude': 0, 'station_longitude': 0,
                 'back_azimuth': 0, 'slowness': 6.4}
        lat_ps, lon_ps = self.model.ppoint(stats, 100, phase='S')
        lat_sp, lon_sp = self.model.ppoint(stats, 100, phase='P')
        self.assertLess(abs(lat_ps-lat_ps_xy)/lat_ps_xy, 0.05)
        self.assertLess(abs(lat_sp-lat_sp_xy)/lat_sp_xy, 0.05)
        self.assertLess(abs(lon_ps), 0.0001)
        self.assertLess(abs(lon_sp), 0.0001)

    def test_ppointvsobspytaup_S2P(self):
        slowness = 12.33
        evdep = 12.4
        evdist = 67.7
        pp1 = self.model.ppoint_distance(200, slowness, phase='P')
        model = TauPyModel(model='iasp91')
        arrivals = model.get_ray_paths(evdep, evdist, ('S250p',))
        arrival = arrivals[0]
        index = np.searchsorted(arrival.path['depth'][::-1], 200)
        pdist = arrival.path['dist']
        pp2 = degrees2kilometers((pdist[-1] - pdist[-index-1]) * 180 / np.pi)
        self.assertLess(abs(pp1-pp2)/pp2, 0.2)

    def test_ppointvsobspytaup_P2S(self):
        slowness = 6.28
        evdep = 12.4
        evdist = 67.7
        depth = 200
        pp1 = self.model.ppoint_distance(depth, slowness)
        model = TauPyModel(model='iasp91')
        arrivals = model.get_ray_paths(evdep, evdist, ('P250s',))
        arrival = arrivals[0]
        index = np.searchsorted(arrival.path['depth'][::-1], depth)
        pdist = arrival.path['dist']
        pp2 = degrees2kilometers((pdist[-1] - pdist[-index-1]) * 180 / np.pi)
        self.assertLess(abs(pp1-pp2)/pp2, 0.1)

    def test_moveout_vs_XY(self):
        stream = read_rf()[:1]
        for tr in stream:
            tr.stats.slowness = 10.
            tr.stats.onset = tr.stats.starttime + 20.643
        stream.decimate(10)
        N = len(stream[0])
        t = np.linspace(0, 20*np.pi, N)
        stream[0].data = np.sin(t)*np.exp(-0.04*t)
        stream[0].stats.slowness = 4.0
        stream1 = stream.copy()
        stream2 = stream.copy()
        stream3 = stream.copy()
        stream3[0].stats.slowness = 9.0
        stream4 = stream3.copy()
        stream5 = stream.copy()
        stream6 = stream.copy()
        stream7 = stream.copy()
        stream8 = stream.copy()
        stream9 = stream.copy()
        stream10 = stream.copy()

        stream1.moveout()
        stream3.moveout()
        stream5.moveout(phase='Ppps')
        stream7.moveout(phase='Ppss')
        stream9.moveout(phase='Psss')
#        stream2._moveout_xy()
#        print(repr(stream2[0].data))
#        stream4._moveout_xy()
#        print(repr(stream6[0].data))
#        stream6._moveout_xy(phase='Ppps')
#        print(repr(stream6[0].data))
#        stream8._moveout_xy(phase='Ppss')
#        print(repr(stream8[0].data))
#        stream10._moveout_xy(phase='Psss')
#        print(repr(stream10[0].data))
        stream2[0].data = XY_PSMOUT_REF4
        stream4[0].data = XY_PSMOUT_REF9
        stream6[0].data = XY_PPPSMOUT_REF4
        stream8[0].data = XY_PPSSMOUT_REF4
        stream8[0].data = XY_PSSSMOUT_REF4
        np.testing.assert_array_almost_equal(stream1[0].data, stream2[0].data,
                                             decimal=2)
        np.testing.assert_array_almost_equal(stream3[0].data, stream4[0].data,
                                             decimal=2)
        np.testing.assert_array_almost_equal(stream5[0].data, stream6[0].data,
                                             decimal=2)
        np.testing.assert_array_almost_equal(stream7[0].data, stream8[0].data,
                                             decimal=2)
        np.testing.assert_array_almost_equal(stream9[0].data, stream10[0].data,
                                             decimal=2)
#        import pylab
#        pylab.plot(t, stream[0].data)
#        pylab.plot(t, stream1[0].data)
#        pylab.plot(t, stream2[0].data)
#        pylab.plot(t, stream3[0].data)
#        pylab.plot(t, stream4[0].data)
#        pylab.show()


XY_PSMOUT_REF4 = np.array([
        0.        ,  0.20685077,  0.40121415,  0.57480496,  0.72038388,
        0.83205634,  0.90550762,  0.93816525,  0.92928219,  0.87993914,
        0.79296678,  0.67279297,  0.52522254,  0.35716093,  0.17629366,
       -0.00926218, -0.19131993, -0.36198229, -0.51398158, -0.6409868 ,
       -0.73786467, -0.80088407, -0.82785559, -0.81820154, -0.77295434,
       -0.69468468, -0.58736324, -0.45616412, -0.30721858, -0.1473311 ,
        0.01632907,  0.17654736,  0.3263799 ,  0.45945233,  0.57022905,
        0.65424103,  0.70826316,  0.73043478,  0.72031802,  0.67889321,
        0.60849249,  0.51267523,  0.3960523 ,  0.2640667 ,  0.12274211,
       -0.02159013, -0.1625728 , -0.29410103, -0.41058487, -0.50718498,
       -0.58001149, -0.62627846, -0.6444068 , -0.63407338, -0.59620428,
       -0.53291333, -0.44739008, -0.34374234, -0.22680151, -0.10189932,
        0.02537351,  0.14941582,  0.26486105,  0.36680773,  0.45102602,
        0.51413125,  0.55371773,  0.56844777,  0.55809206,  0.52352124,
        0.46664971,  0.39033449,  0.29823449,  0.19463754,  0.08426227,
       -0.0279551 , -0.13708013, -0.2383958 , -0.32760495, -0.40101117,
       -0.45567009, -0.4895058 , -0.50138688, -0.49116006, -0.45964089,
       -0.40856159, -0.34048039, -0.2586557 , -0.16689225, -0.06936564,
        0.02956628,  0.12555695,  0.21446076,  0.2925109 ,  0.35647765,
        0.40380055,  0.43268913,  0.44218832,  0.43220624,  0.40350389,
        0.35764757,  0.29692709,  0.22424364,  0.14297281,  0.05680914,
       -0.03040059, -0.11482802, -0.19283019, -0.26110566, -0.31683305,
       -0.35778633, -0.38242221, -0.38993621, -0.38028535, -0.35417756,
       -0.31302801, -0.25888565, -0.19433302, -0.12236449, -0.04624859,
        0.03061939,  0.10486791,  0.17329611,  0.2330108 ,  0.28154781,
        0.31697252,  0.3379555 ,  0.3438206 ,  0.33456352,  0.31084087,
        0.27393049,  0.22566511,  0.16834314,  0.10462047,  0.03738835,
       -0.03035677, -0.09564599, -0.15566723, -0.20788547, -0.25014895,
       -0.28077677, -0.29862452, -0.30312535, -0.29430506, -0.27277118,
       -0.23967662, -0.19666031, -0.14576738, -0.08935307, -0.02997464,
        0.02972374,  0.08712804,  0.13976802,  0.18542282,  0.22221385,
        0.24868117,  0.26384032,  0.26721737,  0.25886115,  0.23933244,
        0.20967086,  0.17134148,  0.12616374,  0.076226  ,  0.0237898 ,
       -0.02881182, -0.07927751, -0.1254376 , -0.16534677, -0.19736524,
       -0.22022539, -0.23308098, -0.23553701, -0.22765951, -0.20996499,
       -0.18339032, -0.14924482, -0.1091468 , -0.0649477 , -0.01864733,
        0.02769604,  0.07205657,  0.11252882,  0.14740905,  0.17526627,
        0.19500025,  0.20588405,  0.20758964,  0.20019546,  0.18417633,
        0.16037606,  0.12996438,  0.09438046,  0.05526548,  0.01438756,
       -0.02643761, -0.06542692, -0.1009072 , -0.13138652, -0.15561636,
       -0.1726421 , -0.18183982, -0.18293811, -0.176024  , -0.16153321,
       -0.14022525, -0.11314489, -0.08197714, -0.0481246 , -0.01277319,
        0.02257201,  0.05642904,  0.08740096,  0.11423281,  0.1358622 ,
        0.15146065,  0.16046508,  0.1625971 ,  0.15787056,  0.14658658,
        0.12931655,  0.10687447,  0.08027901,  0.05070788,  0.0194462 ,
       -0.01216889, -0.04280522, -0.07119123, -0.0961683 , -0.1167376 ,
       -0.13209991, -0.13849258, -0.14190468, -0.13933662, -0.13103753,
       -0.11744326, -0.09920098, -0.07713933, -0.0522316 , -0.02555352,
        0.00176362,  0.02857922,  0.05379169,  0.07638259,  0.09545758,
        0.11028155,  0.12030612,  0.12518986,  0.12480893,  0.11929093,
        0.10897356,  0.09440514,  0.07625975,  0.05531133,  0.03244196,
        0.00857653, -0.01531183, -0.03826171, -0.05936159, -0.07778627,
       -0.09282808, -0.10392399, -0.11067647, -0.11037307, -0.10794661,
       -0.10121839, -0.09052543, -0.07635763, -0.05933614, -0.0401867 ,
       -0.0197084 ,  0.00125777,  0.02186427,  0.04128937,  0.05877133,
        0.0736364 ,  0.08532503,  0.09341235,  0.09762333,  0.09784179,
        0.09411285,  0.08663912,  0.07577042,  0.06198828,  0.04588466,
        0.02813708,  0.0094807 , -0.00932199, -0.02652212, -0.04291547,
       -0.05732708, -0.06921121, -0.07813137, -0.08377568, -0.08596779,
       -0.08467161, -0.07999071, -0.07216223, -0.06154547, -0.0486056 ])


XY_PSMOUT_REF9 = np.array([
         0.00000000e+00,   2.06850767e-01,   4.01214153e-01,
         5.74804962e-01,   7.20383883e-01,   8.32056344e-01,
         9.05507624e-01,   9.38165247e-01,   9.29282188e-01,
         8.79939139e-01,   7.92966783e-01,   6.72792971e-01,
         5.25222540e-01,   3.57160926e-01,   1.76293656e-01,
        -9.26217809e-03,  -1.91319928e-01,  -3.61982286e-01,
        -5.13981581e-01,  -6.40986800e-01,  -7.37864673e-01,
        -8.00884068e-01,  -8.27855587e-01,  -8.18201542e-01,
        -7.72954345e-01,  -6.94684684e-01,  -5.87363243e-01,
        -4.56164122e-01,  -3.07218581e-01,  -1.47331104e-01,
         1.63290743e-02,   1.76547363e-01,   3.26379895e-01,
         4.59452331e-01,   5.70229053e-01,   6.54241025e-01,
         7.08263159e-01,   7.30434775e-01,   7.20318019e-01,
         6.78893209e-01,   6.08492494e-01,   5.12675226e-01,
         3.96052301e-01,   2.64066696e-01,   1.22742109e-01,
        -2.15901304e-02,  -1.62572801e-01,  -2.94101030e-01,
        -4.10584867e-01,  -5.07184982e-01,  -5.80011487e-01,
        -6.26278460e-01,  -6.44406796e-01,  -6.34073377e-01,
        -5.96204281e-01,  -5.32913327e-01,  -4.47390079e-01,
        -3.43742341e-01,  -2.26801515e-01,  -1.01899318e-01,
         2.53735073e-02,   1.49415821e-01,   2.64861047e-01,
         3.66807729e-01,   4.51026022e-01,   5.14131248e-01,
         5.53717732e-01,   5.68447769e-01,   5.58092058e-01,
         5.23521245e-01,   4.66649711e-01,   3.90334487e-01,
         2.98234493e-01,   1.94637537e-01,   8.42622668e-02,
        -2.79550962e-02,  -1.37080133e-01,  -2.38395795e-01,
        -3.27604949e-01,  -4.01011169e-01,  -4.55670089e-01,
        -4.89505798e-01,  -5.01386881e-01,  -4.91160065e-01,
        -4.59640890e-01,  -4.08561587e-01,  -3.40480387e-01,
        -2.58655697e-01,  -1.66892245e-01,  -6.93656430e-02,
         2.95662843e-02,   1.25556946e-01,   2.14460760e-01,
         2.92510897e-01,   3.56477648e-01,   4.03800547e-01,
         4.32689130e-01,   4.42188323e-01,   4.32206243e-01,
         4.03503895e-01,   3.57647568e-01,   2.96927094e-01,
         2.24243641e-01,   1.42972812e-01,   5.68091385e-02,
        -3.04005928e-02,  -1.14828020e-01,  -1.92830190e-01,
        -2.61105657e-01,  -3.16833049e-01,  -3.57786328e-01,
        -3.82422209e-01,  -3.89936209e-01,  -3.80285352e-01,
        -3.54177564e-01,  -3.13028008e-01,  -2.58885652e-01,
        -1.94333017e-01,  -1.22364491e-01,  -4.62485924e-02,
         3.06193884e-02,   1.04867913e-01,   1.73296109e-01,
         2.33010799e-01,   2.81547815e-01,   3.16972524e-01,
         3.37955505e-01,   3.43820602e-01,   3.34563524e-01,
         3.10840875e-01,   2.73930490e-01,   2.25665107e-01,
         1.68343142e-01,   1.04620472e-01,   3.73883545e-02,
        -3.03567685e-02,  -9.56459939e-02,  -1.55667230e-01,
        -2.07885474e-01,  -2.50148952e-01,  -2.80776769e-01,
        -2.98624516e-01,  -3.03125352e-01,  -2.94305056e-01,
        -2.72771180e-01,  -2.39676625e-01,  -1.96660310e-01,
        -1.45767376e-01,  -8.93530697e-02,  -2.99746431e-02,
         2.97237448e-02,   8.71280432e-02,   1.39768019e-01,
         1.85422823e-01,   2.22213849e-01,   2.48681173e-01,
         2.63840318e-01,   2.67217368e-01,   2.58861154e-01,
         2.39332438e-01,   2.09670857e-01,   1.71341479e-01,
         1.26163736e-01,   7.62260035e-02,   2.37898044e-02,
        -2.88118199e-02,  -7.92775080e-02,  -1.25437602e-01,
        -1.65346771e-01,  -1.97365239e-01,  -2.20225394e-01,
        -2.33080983e-01,  -2.35537007e-01,  -2.27659509e-01,
        -2.09964991e-01,  -1.83390319e-01,  -1.49244815e-01,
        -1.09146804e-01,  -6.49477020e-02,  -1.86473317e-02,
         2.76960414e-02,   7.20565692e-02,   1.12528823e-01,
         1.47409052e-01,   1.75266266e-01,   1.95000246e-01,
         2.05884054e-01,   2.07589641e-01,   2.00195462e-01,
         1.84176326e-01,   1.60376057e-01,   1.29964381e-01,
         9.43804607e-02,   5.52654788e-02,   1.43875573e-02,
        -2.64376123e-02,  -6.54269159e-02,  -1.00907199e-01,
        -1.31386518e-01,  -1.55616358e-01,  -1.72642097e-01,
        -1.81839824e-01,  -1.82938114e-01,  -1.76024005e-01,
        -1.61533207e-01,  -1.40225247e-01,  -1.13144889e-01,
        -8.08569267e-02,  -4.49075997e-02,  -7.52503192e-03,
         2.95191947e-02,   6.45018071e-02,   9.58266556e-02,
         1.22097038e-01,   1.42176777e-01,   1.55238688e-01,
         1.60797343e-01,   1.58725709e-01,   1.49254858e-01,
         1.32956862e-01,   1.10712238e-01,   8.48945975e-02,
         5.36934510e-02,   2.06091292e-02,  -1.27803776e-02,
        -4.49136645e-02,  -7.43179023e-02,  -9.96754393e-02,
        -1.19882479e-01,  -1.34095713e-01,  -1.41767040e-01,
        -1.42661259e-01,  -1.36860386e-01,  -1.24660127e-01,
        -1.06697001e-01,  -8.39871317e-02,  -5.77009395e-02,
        -2.91562229e-02,   2.46766023e-04,   2.90924795e-02,
         5.60179539e-02,   7.97758251e-02,   9.92914438e-02,
         1.13710836e-01,   1.22436620e-01,   1.27644032e-01,
         1.23927720e-01,   1.14390202e-01,   9.96028483e-02,
         8.02256018e-02,   5.72616309e-02,   3.17927226e-02,
         5.14358096e-03,  -2.12685559e-02,  -4.61105555e-02,
        -6.81217089e-02,  -8.62581506e-02,  -9.96882468e-02,
        -1.07828774e-01,  -1.10369943e-01,  -1.09221406e-01,
        -1.00233890e-01,  -8.64219144e-02,  -6.85789958e-02,
        -4.76815179e-02,  -2.48361435e-02,  -1.22363481e-03,
         2.19616070e-02,   4.35691364e-02,   6.25495091e-02,
         7.80034214e-02,   8.92233625e-02,   9.77994800e-02,
         9.89592373e-02,   9.51236114e-02,   8.65948722e-02,
         7.39008114e-02,   5.77637255e-02,   3.90621126e-02,
         1.87827852e-02,  -2.02812580e-03,  -2.23194398e-02,
        -4.10855636e-02,  -5.74153624e-02,  -7.05360845e-02,
        -8.15057531e-02,  -8.63377601e-02,  -8.67172778e-02,
        -8.27238709e-02,  -7.46516809e-02,  -6.29909113e-02,
        -4.83990796e-02,  -3.16662192e-02,  -1.36721665e-02,
         0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
         0.00000000e+00,   0.00000000e+00,   0.00000000e+00])


XY_PPPSMOUT_REF4 = np.array([
        0.        ,  0.20685077,  0.40121415,  0.57480496,  0.72038388,
        0.83205634,  0.90550762,  0.93816525,  0.92928219,  0.87993914,
        0.79296678,  0.67279297,  0.52522254,  0.35716093,  0.17629366,
       -0.00926218, -0.19131993, -0.36198229, -0.51398158, -0.6409868 ,
       -0.73786467, -0.80088407, -0.82785559, -0.81820154, -0.77295434,
       -0.69468468, -0.58736324, -0.45616412, -0.30721858, -0.1473311 ,
        0.01632907,  0.17654736,  0.3263799 ,  0.45945233,  0.57022905,
        0.65424103,  0.70826316,  0.73043478,  0.72031802,  0.67889321,
        0.60849249,  0.51267523,  0.3960523 ,  0.2640667 ,  0.12274211,
       -0.02159013, -0.1625728 , -0.29410103, -0.41058487, -0.50718498,
       -0.58001149, -0.62627846, -0.6444068 , -0.63407338, -0.59620428,
       -0.53291333, -0.44739008, -0.34374234, -0.22680151, -0.10189932,
        0.02537351,  0.14941582,  0.26486105,  0.36680773,  0.45102602,
        0.51413125,  0.55371773,  0.56844777,  0.55809206,  0.52352124,
        0.46664971,  0.39033449,  0.29823449,  0.19463754,  0.08426227,
       -0.0279551 , -0.13708013, -0.2383958 , -0.32760495, -0.40101117,
       -0.45567009, -0.4895058 , -0.50138688, -0.49116006, -0.45964089,
       -0.40856159, -0.34048039, -0.2586557 , -0.16689225, -0.06936564,
        0.02956628,  0.12555695,  0.21446076,  0.2925109 ,  0.35647765,
        0.40380055,  0.43268913,  0.44218832,  0.43220624,  0.40350389,
        0.35764757,  0.29692709,  0.22424364,  0.14297281,  0.05680914,
       -0.03040059, -0.11482802, -0.19283019, -0.26110566, -0.31683305,
       -0.35778633, -0.38242221, -0.38993621, -0.38028535, -0.35417756,
       -0.31302801, -0.25888565, -0.19433302, -0.12236449, -0.04624859,
        0.03061939,  0.10486791,  0.17329611,  0.2330108 ,  0.28154781,
        0.31697252,  0.3379555 ,  0.3438206 ,  0.33456352,  0.31084087,
        0.27393049,  0.22566511,  0.16834314,  0.10462047,  0.03738835,
       -0.03035677, -0.09564599, -0.15566723, -0.20788547, -0.25014895,
       -0.28077677, -0.29862452, -0.30312535, -0.29430506, -0.27277118,
       -0.23967662, -0.19666031, -0.14576738, -0.08935307, -0.02997464,
        0.02972374,  0.08712804,  0.13976802,  0.18542282,  0.22221385,
        0.24868117,  0.26384032,  0.26721737,  0.25886115,  0.23933244,
        0.20967086,  0.17134148,  0.12616374,  0.076226  ,  0.0237898 ,
       -0.02881182, -0.07927751, -0.1254376 , -0.16534677, -0.19736524,
       -0.22022539, -0.23308098, -0.23553701, -0.22765951, -0.20996499,
       -0.18339032, -0.14924482, -0.1091468 , -0.0649477 , -0.01864733,
        0.02769604,  0.07205657,  0.11252882,  0.14740905,  0.17526627,
        0.19500025,  0.20588405,  0.20758964,  0.20019546,  0.18417633,
        0.16037606,  0.12996438,  0.09438046,  0.05526548,  0.01438756,
       -0.02643761, -0.06542692, -0.1009072 , -0.13138652, -0.15561636,
       -0.1726421 , -0.18183982, -0.18293811, -0.176024  , -0.16153321,
       -0.14022525, -0.11314489, -0.08115784, -0.04577175, -0.00893501,
        0.02765246,  0.06233223,  0.09356184,  0.11998277,  0.14047883,
        0.15422264,  0.16070797,  0.15976718,  0.1515729 ,  0.13662441,
        0.11571912,  0.08991124,  0.06045944,  0.0287662 , -0.00368849,
       -0.0354157 , -0.06498493, -0.09108818, -0.11259753, -0.12861326,
       -0.13850066, -0.14492126, -0.14151643, -0.13174942, -0.11618166,
       -0.09562664, -0.07110964, -0.04381669, -0.0150375 ,  0.0138938 ,
        0.04166133,  0.0670256 ,  0.0888789 ,  0.10629332,  0.1185587 ,
        0.12521179,  0.12605236,  0.12114763,  0.11082444,  0.09564975,
        0.07640033,  0.05402431,  0.0295941 ,  0.00425709, -0.02081943,
       -0.04450028, -0.0657339 , -0.08359922, -0.09734369, -0.10641567,
       -0.11048553, -0.10945655, -0.1034653 , -0.09287148, -0.0782376 ,
       -0.06029974, -0.03993164, -0.01810156,  0.00417201,  0.02586858,
        0.04601131,  0.06371095,  0.07820489,  0.08888867,  0.09534203,
        0.09734396,  0.09487965,  0.08813752,  0.07894236,  0.06455666,
        0.04750805,  0.02861942,  0.00878207, -0.01108569, -0.0300818 ,
       -0.04735978, -0.06216709, -0.07387679, -0.08201403, -0.08627486,
       -0.08653653, -0.08286019, -0.07548461, -0.06481224, -0.05138734,
       -0.03587009, -0.019003  ,  0.        ,  0.        ,  0.        ])

XY_PPSSMOUT_REF4 = np.array([
        0.        ,  0.20685077,  0.40121415,  0.57480496,  0.72038388,
        0.83205634,  0.90550762,  0.93816525,  0.92928219,  0.87993914,
        0.79296678,  0.67279297,  0.52522254,  0.35716093,  0.17629366,
       -0.00926218, -0.19131993, -0.36198229, -0.51398158, -0.6409868 ,
       -0.73786467, -0.80088407, -0.82785559, -0.81820154, -0.77295434,
       -0.69468468, -0.58736324, -0.45616412, -0.30721858, -0.1473311 ,
        0.01632907,  0.17654736,  0.3263799 ,  0.45945233,  0.57022905,
        0.65424103,  0.70826316,  0.73043478,  0.72031802,  0.67889321,
        0.60849249,  0.51267523,  0.3960523 ,  0.2640667 ,  0.12274211,
       -0.02159013, -0.1625728 , -0.29410103, -0.41058487, -0.50718498,
       -0.58001149, -0.62627846, -0.6444068 , -0.63407338, -0.59620428,
       -0.53291333, -0.44739008, -0.34374234, -0.22680151, -0.10189932,
        0.02537351,  0.14941582,  0.26486105,  0.36680773,  0.45102602,
        0.51413125,  0.55371773,  0.56844777,  0.55809206,  0.52352124,
        0.46664971,  0.39033449,  0.29823449,  0.19463754,  0.08426227,
       -0.0279551 , -0.13708013, -0.2383958 , -0.32760495, -0.40101117,
       -0.45567009, -0.4895058 , -0.50138688, -0.49116006, -0.45964089,
       -0.40856159, -0.34048039, -0.2586557 , -0.16689225, -0.06936564,
        0.02956628,  0.12555695,  0.21446076,  0.2925109 ,  0.35647765,
        0.40380055,  0.43268913,  0.44218832,  0.43220624,  0.40350389,
        0.35764757,  0.29692709,  0.22424364,  0.14297281,  0.05680914,
       -0.03040059, -0.11482802, -0.19283019, -0.26110566, -0.31683305,
       -0.35778633, -0.38242221, -0.38993621, -0.38028535, -0.35417756,
       -0.31302801, -0.25888565, -0.19433302, -0.12236449, -0.04624859,
        0.03061939,  0.10486791,  0.17329611,  0.2330108 ,  0.28154781,
        0.31697252,  0.3379555 ,  0.3438206 ,  0.33456352,  0.31084087,
        0.27393049,  0.22566511,  0.16834314,  0.10462047,  0.03738835,
       -0.03035677, -0.09564599, -0.15566723, -0.20788547, -0.25014895,
       -0.28077677, -0.29862452, -0.30312535, -0.29430506, -0.27277118,
       -0.23967662, -0.19666031, -0.14576738, -0.08935307, -0.02997464,
        0.02972374,  0.08712804,  0.13976802,  0.18542282,  0.22221385,
        0.24868117,  0.26384032,  0.26721737,  0.25886115,  0.23933244,
        0.20967086,  0.17134148,  0.12616374,  0.076226  ,  0.0237898 ,
       -0.02881182, -0.07927751, -0.1254376 , -0.16534677, -0.19736524,
       -0.22022539, -0.23308098, -0.23553701, -0.22765951, -0.20996499,
       -0.18339032, -0.14924482, -0.1091468 , -0.0649477 , -0.01864733,
        0.02769604,  0.07205657,  0.11252882,  0.14740905,  0.17526627,
        0.19500025,  0.20588405,  0.20758964,  0.20019546,  0.18417633,
        0.16037606,  0.12996438,  0.09438046,  0.05526548,  0.01438756,
       -0.02643761, -0.06542692, -0.1009072 , -0.13138652, -0.15561636,
       -0.1726421 , -0.18183982, -0.18293811, -0.176024  , -0.16153321,
       -0.14022525, -0.11314489, -0.08133949, -0.0462934 , -0.00978595,
        0.02652616,  0.06102362,  0.09219618,  0.11870827,  0.13945559,
        0.15361048,  0.16065414,  0.1603944 ,  0.1529687 ,  0.13883236,
        0.1187326 ,  0.09367044,  0.06485137,  0.03362807,  0.00143742,
       -0.0302651 , -0.0600708 , -0.08667985, -0.10895757, -0.12598225,
       -0.13708264, -0.14186375, -0.14021972, -0.13233368, -0.11866458,
       -0.09992211, -0.07703057, -0.05108394, -0.02329418,  0.00506498,
        0.03271607,  0.0584348 ,  0.08110409,  0.09976218,  0.11364268,
        0.12220585,  0.12515877,  0.12246422,  0.11433806,  0.10314781,
        0.08525584,  0.06387556,  0.04002329,  0.01480795, -0.01062059,
       -0.03512307, -0.05762188, -0.07714805, -0.09288218, -0.10418896,
       -0.11064179, -0.11203843, -0.10840578, -0.09999506, -0.08726613,
       -0.07086372, -0.05158526, -0.03034208, -0.008118  ,  0.01407718,
        0.0352526 ,  0.05448024,  0.0709357 ,  0.08393238,  0.09295054,
        0.09765707,  0.09791736,  0.09379756,  0.08555851,  0.07364035,
        0.05863981,  0.04128122,  0.02238088,  0.00281064, -0.01654369,
       -0.0348209 , -0.05122316, -0.06505033, -0.07572906, -0.08283724,
       -0.08611909, -0.08549444, -0.0810589 , -0.07307705, -0.06196686,
       -0.04827898, -0.03267021, -0.0158708 ,  0.        ,  0.        ])


XY_PSSSMOUT_REF4 = np.array([
        0.        ,  0.20685077,  0.40121415,  0.57480496,  0.72038388,
        0.83205634,  0.90550762,  0.93816525,  0.92928219,  0.87993914,
        0.79296678,  0.67279297,  0.52522254,  0.35716093,  0.17629366,
       -0.00926218, -0.19131993, -0.36198229, -0.51398158, -0.6409868 ,
       -0.73786467, -0.80088407, -0.82785559, -0.81820154, -0.77295434,
       -0.69468468, -0.58736324, -0.45616412, -0.30721858, -0.1473311 ,
        0.01632907,  0.17654736,  0.3263799 ,  0.45945233,  0.57022905,
        0.65424103,  0.70826316,  0.73043478,  0.72031802,  0.67889321,
        0.60849249,  0.51267523,  0.3960523 ,  0.2640667 ,  0.12274211,
       -0.02159013, -0.1625728 , -0.29410103, -0.41058487, -0.50718498,
       -0.58001149, -0.62627846, -0.6444068 , -0.63407338, -0.59620428,
       -0.53291333, -0.44739008, -0.34374234, -0.22680151, -0.10189932,
        0.02537351,  0.14941582,  0.26486105,  0.36680773,  0.45102602,
        0.51413125,  0.55371773,  0.56844777,  0.55809206,  0.52352124,
        0.46664971,  0.39033449,  0.29823449,  0.19463754,  0.08426227,
       -0.0279551 , -0.13708013, -0.2383958 , -0.32760495, -0.40101117,
       -0.45567009, -0.4895058 , -0.50138688, -0.49116006, -0.45964089,
       -0.40856159, -0.34048039, -0.2586557 , -0.16689225, -0.06936564,
        0.02956628,  0.12555695,  0.21446076,  0.2925109 ,  0.35647765,
        0.40380055,  0.43268913,  0.44218832,  0.43220624,  0.40350389,
        0.35764757,  0.29692709,  0.22424364,  0.14297281,  0.05680914,
       -0.03040059, -0.11482802, -0.19283019, -0.26110566, -0.31683305,
       -0.35778633, -0.38242221, -0.38993621, -0.38028535, -0.35417756,
       -0.31302801, -0.25888565, -0.19433302, -0.12236449, -0.04624859,
        0.03061939,  0.10486791,  0.17329611,  0.2330108 ,  0.28154781,
        0.31697252,  0.3379555 ,  0.3438206 ,  0.33456352,  0.31084087,
        0.27393049,  0.22566511,  0.16834314,  0.10462047,  0.03738835,
       -0.03035677, -0.09564599, -0.15566723, -0.20788547, -0.25014895,
       -0.28077677, -0.29862452, -0.30312535, -0.29430506, -0.27277118,
       -0.23967662, -0.19666031, -0.14576738, -0.08935307, -0.02997464,
        0.02972374,  0.08712804,  0.13976802,  0.18542282,  0.22221385,
        0.24868117,  0.26384032,  0.26721737,  0.25886115,  0.23933244,
        0.20967086,  0.17134148,  0.12616374,  0.076226  ,  0.0237898 ,
       -0.02881182, -0.07927751, -0.1254376 , -0.16534677, -0.19736524,
       -0.22022539, -0.23308098, -0.23553701, -0.22765951, -0.20996499,
       -0.18339032, -0.14924482, -0.1091468 , -0.0649477 , -0.01864733,
        0.02769604,  0.07205657,  0.11252882,  0.14740905,  0.17526627,
        0.19500025,  0.20588405,  0.20758964,  0.20019546,  0.18417633,
        0.16037606,  0.12996438,  0.09438046,  0.05526548,  0.01438756,
       -0.02643761, -0.06542692, -0.1009072 , -0.13138652, -0.15561636,
       -0.1726421 , -0.18183982, -0.18293811, -0.176024  , -0.16153321,
       -0.14022525, -0.11314489, -0.08133949, -0.0462934 , -0.00978595,
        0.02652616,  0.06102362,  0.09219618,  0.11870827,  0.13945559,
        0.15361048,  0.16065414,  0.1603944 ,  0.1529687 ,  0.13883236,
        0.1187326 ,  0.09367044,  0.06485137,  0.03362807,  0.00143742,
       -0.0302651 , -0.0600708 , -0.08667985, -0.10895757, -0.12598225,
       -0.13708264, -0.14186375, -0.14021972, -0.13233368, -0.11866458,
       -0.09992211, -0.07703057, -0.05108394, -0.02329418,  0.00506498,
        0.03271607,  0.0584348 ,  0.08110409,  0.09976218,  0.11364268,
        0.12220585,  0.12515877,  0.12246422,  0.11433806,  0.10314781,
        0.08525584,  0.06387556,  0.04002329,  0.01480795, -0.01062059,
       -0.03512307, -0.05762188, -0.07714805, -0.09288218, -0.10418896,
       -0.11064179, -0.11203843, -0.10840578, -0.09999506, -0.08726613,
       -0.07086372, -0.05158526, -0.03034208, -0.008118  ,  0.01407718,
        0.0352526 ,  0.05448024,  0.0709357 ,  0.08393238,  0.09295054,
        0.09765707,  0.09791736,  0.09379756,  0.08555851,  0.07364035,
        0.05863981,  0.04128122,  0.02238088,  0.00281064, -0.01654369,
       -0.0348209 , -0.05122316, -0.06505033, -0.07572906, -0.08283724,
       -0.08611909, -0.08549444, -0.0810589 , -0.07307705, -0.06196686,
       -0.04827898, -0.03267021, -0.0158708 ,  0.        ,  0.        ])


def suite():
    return unittest.makeSuite(SimpleModelTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
