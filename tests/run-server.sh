export FRIGG_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" && cd .. && pwd )

PYTHONPATH=$FRIGG_ROOT:$PYTHONPATH python -m frigg.main $@