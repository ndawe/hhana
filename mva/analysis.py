import random
from collections import namedtuple

import numpy as np

from rootpy.stats import histfactory
from rootpy.plotting import Hist

from . import samples, log; log = log[__name__]
from .norm import cache as norm_cache
from .categories import CATEGORIES
from .stats.utils import efficiency_cut
from .classify import histogram_scores


Scores = namedtuple('Scores', [
    'data',
    'data_scores',
    'bkg_scores',
    'all_sig_scores',
    'min_score',
    'max_score',])


class Analysis(object):

    def __init__(self, year,
                 systematics=False,
                 use_embedding=False,
                 target_region='OS_TRK',
                 qcd_shape_region='nOS',
                 fit_param='TRACK',
                 random_mu=False,
                 mu=1.,
                 mpl=False):

        self.year = year
        self.systematics = systematics
        self.use_embedding = use_embedding
        self.target_region = target_region
        self.qcd_shape_region = qcd_shape_region
        self.fit_param = fit_param
        self.mpl = mpl

        if use_embedding:
            log.info("Using embedded Ztautau")
            self.ztautau = samples.Embedded_Ztautau(
                year=year,
                systematics=systematics,
                mpl=mpl)
        else:
            log.info("Using ALPGEN Ztautau")
            self.ztautau = samples.MC_Ztautau(
                year=year,
                systematics=systematics,
                mpl=mpl)

        self.others = samples.Others(
            year=year,
            systematics=systematics,
            mpl=mpl)

        if random_mu:
            log.info("using a random mu (signal strength)")
            self.mu = random.uniform(10, 1000)
        else:
            log.info("using a mu (signal strength) of {0:.1f}".format(mu))
            self.mu = mu

        self.data = samples.Data(year=year, mpl=mpl)

        self.higgs_125 = samples.Higgs(
            year=year,
            mass=125,
            systematics=systematics,
            linecolor='red',
            linewidth=2,
            linestyle='dashed',
            mpl=mpl,
            scale=self.mu)

        # QCD shape region SS or !OS
        self.qcd = samples.QCD(
            data=self.data,
            mc=[self.ztautau, self.others],
            shape_region=qcd_shape_region,
            mpl=mpl)

        self.qcd.scale = 1.
        self.ztautau.scale = 1.

        self.backgrounds = [
            self.qcd,
            self.others,
            self.ztautau,
        ]

        self.signals = self.get_signals(125)

    def get_signals(self, mass=125, mode=None):

        signals = []
        if mode == 'combined':
            signals.append(samples.Higgs(
                year=self.year,
                mass=mass,
                systematics=self.systematics,
                mpl=self.mpl,
                scale=self.mu,
                linecolor='red',
                linewidth=2,
                linestyle='dashed'))
            return signals
        elif mode is None:
            for modes in samples.Higgs.MODES_COMBINED:
                signals.append(samples.Higgs(
                    year=self.year,
                    modes=modes,
                    mass=mass,
                    systematics=self.systematics,
                    mpl=self.mpl,
                    scale=self.mu))
        else:
            signals.append(samples.Higgs(
                year=self.year,
                mass=mass,
                mode=mode,
                systematics=self.systematics,
                mpl=self.mpl,
                scale=self.mu))
        return signals

    def normalize(self, category, fit_param=None):

        norm_cache.qcd_ztautau_norm(
            ztautau=self.ztautau,
            qcd=self.qcd,
            category=category,
            param=fit_param if fit_param is not None else self.fit_param)

    def iter_categories(self, *definitions, **kwargs):

        names = kwargs.pop('names', None)
        for definition in definitions:
            for category in CATEGORIES[definition]:
                if names is not None and category.name not in names:
                    continue
                log.info("")
                log.info("=" * 40)
                log.info("%s category" % category.name)
                log.info("=" * 40)
                log.info("Cuts: %s" % self.ztautau.cuts(category, self.target_region))
                log.info("Weights: %s" % (', '.join(map(str, self.ztautau.get_weight_branches('NOMINAL')))))
                self.normalize(category)
                yield category

    def get_suffix(self, fit_param='TRACK', suffix=None):

        output_suffix = '_%sfit_%s' % (fit_param.lower(), self.qcd_shape_region)
        if self.use_embedding:
            output_suffix += '_embedding'
        else:
            output_suffix += '_alpgen'
        if suffix:
            output_suffix += '_%s' % suffix
        output_suffix += '_%d' % (self.year % 1E3)
        return  output_suffix
        #if not self.systematics:
        #    output_suffix += '_statsonly'

    def get_channel(self, hist_template, expr_or_clf, category, region,
                    cuts=None,
                    include_signal=True,
                    mass=125,
                    clf=None,
                    min_score=None,
                    max_score=None,
                    systematics=True,
                    unblind=False):

        # TODO: implement blinding
        log.info("constructing channels")
        samples = [self.data] + self.backgrounds
        channel_name = category.name
        suffix = None
        if include_signal:
            suffix = '_%d' % mass
            channel_name += suffix
            samples += self.get_signals(mass)

        # create HistFactory samples
        histfactory_samples = []
        for s in samples:
            sample = s.get_histfactory_sample(
                hist_template, expr_or_clf,
                category, region,
                cuts=cuts,
                clf=clf,
                min_score=min_score,
                max_score=max_score,
                suffix=suffix)
            histfactory_samples.append(sample)

        # create channel for this mass point
        return histfactory.make_channel(
            channel_name, histfactory_samples[1:], data=histfactory_samples[0])

    def get_channel_array(self, vars,
                          category, region,
                          cuts=None,
                          include_signal=True,
                          mass=125,
                          mode=None,
                          clf=None,
                          min_score=None,
                          max_score=None,
                          weighted=True,
                          field_scale=None,
                          weight_hist=None,
                          systematics=True,
                          unblind=False):

        # TODO: implement blinding
        log.info("constructing channels")
        samples = [self.data] + self.backgrounds
        channel_name = category.name
        suffix = None
        if include_signal:
            suffix = '_%d' % mass
            channel_name += suffix
            samples += self.get_signals(mass, mode)

        # create HistFactory samples
        histfactory_samples = []
        for s in samples:
            field_hist = s.get_field_hist(vars)
            field_sample = s.get_histfactory_sample_array(
                field_hist,
                category, region,
                cuts=cuts,
                clf=clf,
                min_score=min_score,
                max_score=max_score,
                weighted=weighted,
                field_scale=field_scale,
                weight_hist=weight_hist,
                systematics=systematics,
                suffix=suffix)
            histfactory_samples.append(field_sample)

        field_channels = {}
        for field in vars.keys():
            # create channel for this mass point
            channel = histfactory.make_channel(
                channel_name + '_{0}'.format(field),
                [s[field] for s in histfactory_samples[1:]],
                data=histfactory_samples[0][field])
            field_channels[field] = channel
        return field_channels

    def get_scores(self, clf, category, region, cuts=None,
                   mass_points=None, mode=None, unblind=False,
                   systematics=True):

        log.info("getting scores")

        min_score = float('inf')
        max_score = float('-inf')

        # data scores
        data_scores = None
        if unblind:
            data_scores, _ = self.data.scores(
                clf,
                category=category,
                region=region,
                cuts=cuts)
            _min = data_scores.min()
            _max = data_scores.max()
            if _min < min_score:
                min_score = _min
            if _max > max_score:
                max_score = _max

        # background model scores
        bkg_scores = []
        for bkg in self.backgrounds:
            scores_dict = bkg.scores(
                clf,
                category=category,
                region=region,
                cuts=cuts,
                systematics=systematics,
                systematics_components=bkg.WORKSPACE_SYSTEMATICS)

            for sys_term, (scores, weights) in scores_dict.items():
                if len(scores) == 0:
                    continue
                _min = np.min(scores)
                _max = np.max(scores)
                if _min < min_score:
                    min_score = _min
                if _max > max_score:
                    max_score = _max

            bkg_scores.append((bkg, scores_dict))

        # signal scores
        all_sig_scores = {}
        if mass_points is not None:
            for mass in samples.Higgs.MASS_POINTS:
                if mass not in mass_points:
                    continue
                # signal scores
                sigs = self.get_signals(mass=mass, mode=mode)
                sig_scores = []
                for sig in sigs:
                    scores_dict = sig.scores(
                        clf,
                        category=category,
                        region=region,
                        cuts=cuts,
                        systematics=systematics,
                        systematics_components=sig.WORKSPACE_SYSTEMATICS)

                    for sys_term, (scores, weights) in scores_dict.items():
                        if len(scores) == 0:
                            continue
                        _min = np.min(scores)
                        _max = np.max(scores)
                        if _min < min_score:
                            min_score = _min
                        if _max > max_score:
                            max_score = _max

                    sig_scores.append((sig, scores_dict))
                all_sig_scores[mass] = sig_scores

        min_score -= 1e-5
        max_score += 1e-5

        log.info("min score: {0} max score: {1}".format(min_score, max_score))
        return Scores(
            data=self.data,
            data_scores=data_scores,
            bkg_scores=bkg_scores,
            all_sig_scores=all_sig_scores,
            min_score=min_score,
            max_score=max_score)

    def clf_channels(self, clf,
                     category, region,
                     cuts=None,
                     hist_template=None,
                     bins=10,
                     mass_points=None,
                     mode=None,
                     mu=1.,
                     systematics=True,
                     unblind=False,
                     hybrid_data=False):
        """
        Return a HistFactory Channel for each mass hypothesis
        """
        log.info("constructing channels")
        channels = dict()

        scores_obj = self.get_scores(
            clf, category, region, cuts=cuts,
            mass_points=mass_points, mode=mode,
            systematics=systematics,
            unblind=unblind)

        data_scores = scores_obj.data_scores
        bkg_scores = scores_obj.bkg_scores
        all_sig_scores = scores_obj.all_sig_scores
        min_score = scores_obj.min_score
        max_score = scores_obj.max_score

        bkg_samples = []
        for s, scores in bkg_scores:
            hist_template = Hist(
                bins, min_score, max_score, title=s.label,
                **s.hist_decor)
            sample = s.get_histfactory_sample(
                hist_template, clf,
                category, region,
                cuts=cuts, scores=scores)
            bkg_samples.append(sample)

        data_sample = None
        if data_scores is not None:
            max_unblind_score = None
            if isinstance(unblind, float):
                """
                max_unblind_score = min([
                    efficiency_cut(
                        sum([histogram_scores(hist_template, scores)
                             for s, scores in all_sig_scores[mass]]), 0.3)
                        for mass in mass_points])
                """
                max_unblind_score = efficiency_cut(
                    sum([histogram_scores(hist_template, scores)
                         for s, scores in all_sig_scores[125]]), unblind)
            hist_template = Hist(
                bins, min_score, max_score, title=self.data.label,
                **self.data.hist_decor)
            data_sample = self.data.get_histfactory_sample(
                hist_template, clf,
                category, region,
                cuts=cuts, scores=data_scores,
                max_score=max_unblind_score)
            if not unblind and hybrid_data:
                # blinded bins filled with S+B, for limit/p0 plots
                # Swagato:
                # We have to make 2 kinds of expected sensitivity plots:
                # blinded sensitivity and unblinded sensitivity.
                # For the first one pure AsimovData is used, for second one I
                # suggest to use Hybrid, because the profiled NP's are not
                # always at 0 pull.
                pass

        if mass_points is None:
            # create channel without signal
            channel = histfactory.make_channel(
                category.name,
                bkg_samples,
                data=data_sample)
            return scores_obj, channel

        # signal scores
        for mass in samples.Higgs.MASS_POINTS:
            if mass not in mass_points:
                continue
            log.info('=' * 20)
            log.info("%d GeV mass hypothesis" % mass)

            # create HistFactory samples
            sig_samples = []
            for s, scores in all_sig_scores[mass]:
                hist_template = Hist(
                    bins, min_score, max_score, title=s.label,
                    **s.hist_decor)
                sample = s.get_histfactory_sample(
                    hist_template, clf,
                    category, region,
                    cuts=cuts, scores=scores)
                sig_samples.append(sample)

            # create channel for this mass point
            channel = histfactory.make_channel(
                "%s_%d" % (category.name, mass),
                bkg_samples + sig_samples,
                data=data_sample)
            channels[mass] = channel

        return scores_obj, channels
