#!/usr/bin/env python
#coding:utf-8
# config.py

import config_default;
import copy;
configs = config_default.configs;

def merge( cfg1, cfg2 ):
	"""
	合并两个配置字典

	>>> c1 = {'a': 1, 'b': 2}
	>>> c2 = {'c': 3, 'a': 4, 'd':{}}
	>>> c3 = merge(c1, c2);
	>>> c1;
	{'a': 1, 'b': 2}
	>>> c3;
	{'a': 4, 'c': 3, 'b': 2, 'd': {}}
	"""
	cfg = copy.deepcopy(cfg1);
	if isinstance( cfg, dict ) and isinstance( cfg2, dict):
		for k,v in cfg2.items():
			if k in cfg.keys() \
				and isinstance( cfg[k], dict) and isinstance(v, dict):
					cfg[k] = merge( cfg[k], cfg2[k]);
			else:
				cfg[k] = v;
	return cfg;


try:
	import config_override;
	configs = merge(configs, config_override.configs);
except ImportError:
	pass;

if __name__ == '__main__':
	import doctest;
	doctest.testmod();
