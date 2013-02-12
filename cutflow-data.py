#!/usr/bin/env python

from mva.cutflow import get_parser, make_cutflow

parser = get_parser()
parser.add_argument('--year', default=2012)
args = parser.parse_args()

from pyAMI.client import AMIClient
from pyAMI.query import get_periods


periods = get_periods(AMIClient(), year=args.year)
# only keep top-level periods (skip M)
periods = [p for p in periods if len(p.name) == 1 and p.status == 'frozen'][:-1]
data_name = 'data%d-JetTauEtmiss' % (args.year % 1e3)

samples = [(p.name, p.name, "{0}-{1}".format(data_name, p.name)) for p in periods]

make_cutflow(samples, args)
