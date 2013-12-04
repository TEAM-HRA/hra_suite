'''
Created on Sep 1, 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    from hra_core.misc import Params
    from hra_math.model.parameters.core_parameters import CoreParameters
    from hra_math.model.parameters.statistic_parameters \
        import StatisticParameters
    from hra_math.model.parameters.filter_parameters import FilterParameters
    from hra_math.model.parameters.file_data_parameters \
        import FileDataParameters
    from hra_math.model.parameters.data_vector_parameters \
        import DataVectorParameters
    from hra_math.model.parameters.poincare_plot_parameters \
        import PoincarePlotParameters
    from hra_math.model.parameters.movie_parameters import MovieParameters
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotParametersManager(PoincarePlotParameters,
                                    DataVectorParameters,
                                    FileDataParameters,
                                    FilterParameters,
                                    StatisticParameters,
                                    MovieParameters):

    def prepareObjectParameters(self, host_object, **params):

        #if no parameters are specified this means all parameters are needed
        if len(params) == 0:
            params = {}
            for _, parameter_name in self.__parameters_ids__():
                params[parameter_name] = host_object

        self.__host_object__ = host_object
        self.__host_object__.params = Params(**params)

        if hasattr(self.__host_object__, 'info_handler'):
            if self.__host_object__.params.info_handler == None:
                if hasattr(self.__host_object__, '__default_info_handler__'):
                    self.__host_object__.params.info_handler \
                            = self.__host_object__.__default_info_handler__

        for class_name, parameter_name in self.__parameters_ids__():
            param_object = getattr(self.__host_object__.params, parameter_name,
                                   None)
            if param_object:
                set_method = getattr(param_object,
                                    'setObject' + class_name, None)
                if set_method:
                    set_method(self.__host_object__)

    def validateParameters(self, check_level=None):

        if not hasattr(self.__host_object__, 'params'):
            return
        if check_level == None:
            check_level = CoreParameters.NORMAL_CHECK_LEVEL
        for class_name, parameter_name in self.__parameters_ids__():
            param_object = getattr(self.__host_object__.params, parameter_name,
                                   None)
            if param_object:
                validate_method = getattr(param_object,
                                    'validate' + class_name, None)
                if validate_method:
                    message = validate_method(check_level)
                    if message:
                        return message
        return self.__validateDependenceParameters__(check_level)

    def parameters_info(self):
        print('Poincare plot parameters:')
        print('*' * 50)
        for class_name, parameter_name in self.__parameters_ids__():
            param_object = getattr(self.__host_object__.params, parameter_name,
                                   None)
            if param_object:
                parameters_info_method = getattr(param_object,
                                    'parameters_info' + class_name, None)
                if parameters_info_method:
                    parameters_info_method()

    def __parameters_ids__(self):
        """
        method returns class names and name identifiers of all parameter
        classes used in poincare plot generator
        """
        return [(DataVectorParameters.__name__, DataVectorParameters.NAME),
                (FileDataParameters.__name__, FileDataParameters.NAME),
                (StatisticParameters.__name__, StatisticParameters.NAME),
                (PoincarePlotParameters.__name__, PoincarePlotParameters.NAME),
                (FilterParameters.__name__, FilterParameters.NAME),
                (MovieParameters.__name__, MovieParameters.NAME)]

    def __validateDependenceParameters__(self, check_level=None):
        """
        method checks dependent parameters
        """
        statistics_parameters = getattr(self.__host_object__.params,
                                        StatisticParameters.NAME, None)

        file_data_parameters = getattr(self.__host_object__.params,
                                        FileDataParameters.NAME, None)
        if not statistics_parameters == None \
            and not file_data_parameters == None:
            if file_data_parameters.output_dir == None \
                and statistics_parameters.summary_statistics_is_selected == False: # @IgnorePep8
                return "At least one summary statistic has to be selected !"
