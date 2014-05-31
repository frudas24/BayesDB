#
#   Copyright (c) 2010-2014, MIT Probabilistic Computing Project
#
#   Lead Developers: Jay Baxter and Dan Lovell
#   Authors: Jay Baxter, Dan Lovell, Baxter Eaves, Vikash Mansinghka
#   Research Leads: Vikash Mansinghka, Patrick Shafto
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import re
import utils
import numpy
import os
import pylab
import matplotlib.cm
import inspect
import operator
import ast

import utils
import functions
import data_utils as du


def filter_column_indices(column_indices, where_conditions, M_c, T, X_L_list, X_D_list, engine):
  return [c_idx for c_idx in column_indices if _is_column_valid(c_idx, where_conditions, M_c, X_L_list, X_D_list, T, engine)]

def _is_column_valid(c_idx, where_conditions, M_c, X_L_list, X_D_list, T, engine):
  for ((func, f_args), op, val) in where_conditions:
    # mutual_info, correlation, and dep_prob all take args=(i,j)
    # col_typicality takes just args=i
    # incoming f_args will be None for col_typicality, j for the three others
    if f_args is not None:
      f_args = (f_args, c_idx)
    else:
      f_args = c_idx
    where_value = func(f_args, None, None, M_c, X_L_list, X_D_list, T, engine)
    return op(where_value, val)
  return True


def order_columns(column_indices, order_by, M_c, X_L_list, X_D_list, T, engine):
  if not order_by:
    return column_indices

  ## Step 2: call order by.
  sorted_column_indices = _column_order_by(column_indices, order_by, M_c, X_L_list, X_D_list, T, engine)
  return sorted_column_indices

def _column_order_by(column_indices, function_list, M_c, X_L_list, X_D_list, T, engine):
  """
  Return the original column indices, but sorted by the individual functions.
  """
  if len(column_indices) == 0 or not function_list:
    return column_indices

  scored_column_indices = list() ## Entries are (score, cidx)
  for c_idx in column_indices:
    ## Apply each function to each cidx to get a #functions-length tuple of scores.
    scores = []
    for (f, f_args, desc) in function_list:

      # mutual_info, correlation, and dep_prob all take args=(i,j)
      # col_typicality takes just args=i
      # incoming f_args will be None for col_typicality, j for the three others
      if f_args:
        f_args = (f_args, c_idx)
      else:
        f_args = c_idx
        
      score = f(f_args, None, None, M_c, X_L_list, X_D_list, T, engine)
      if desc:
        score *= -1
      scores.append(score)
    scored_column_indices.append((tuple(scores), c_idx))
  scored_column_indices.sort(key=lambda tup: tup[0], reverse=False)

  return [tup for tup in scored_column_indices]

def function_description(order_item, M_c):
  function_names = {'_col_typicality': 'typicality',
    '_dependence_probability': 'dependence probability',
    '_correlation': 'correlation',
    '_mutual_information': 'mutual information'
    }

  function_name = function_names[order_item[0].__name__]
  order = 'desc' if order_item[2] else 'desc'

  if function_name == 'typicality':
    description = '%s typicality' % order
  else:
    function_arg = M_c['idx_to_name'][str(order_item[1])]
    description = '%s %s with %s' % (order, function_name, function_arg)

  return description

