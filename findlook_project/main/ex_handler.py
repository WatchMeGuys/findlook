from rest_framework.response import Response
import logging
from loguru import logger
from typing import Optional


logger.add("loguruLogs 2.txt", diagnose=False, backtrace=False, format="{time} {level} {message}",
           level="DEBUG", rotation="1 MB", retention='7 days', compression="zip")
logging.basicConfig(filename="Log.txt", level=logging.DEBUG)

class ExceptionResolver:
    """Класс для обработки ошибок и исключений."""

    @staticmethod
    def get_err_message(error_code: int=1, object_name: Optional[str]='Объект', msg: Optional[None]=None) -> dict:
        """Возвращает сообщение ошибки по ее коду"""

        def get_custom_msg(msg):
            """Возвращает стандартный ответ, либо переданное сообщение при его наличии."""
            return 'Неизвестная ошибка' if not msg else msg

        error_messages_dict = {
        1: {'error_code': 1, 'message': get_custom_msg(msg)},
        2: {'error_code': 2, 'message': 'Данные по запросу не найдены.'},
        3: {'error_code': 3, 'message': 'Ошибка в формате данных. Проверьте правильность введенных данных.'}, # ParseError, DataError
        4: {'error_code': 4, 'message': 'Поле не указано, либо указано неверно. Проверьте правильность введенных данных.'}, # ValidationError
        5: {'error_code': 5, 'message': f'{object_name} с таким id уже присутствует в базе данных.'}, # IntegrityError, ValidationError
        6: {'error_code': 6, 'message': f'{object_name} с таким id отсутствует в базе данных.'}, # model.DoesNotExist
        7: {'error_code': 7, 'message': 'Возможно отсутсвует заголовок запроса или поле данных в теле запроса.'}, # KeyError
        8: {'error_code': 8, 'message': get_custom_msg(msg)} # TypeError
        }
        try:
            return error_messages_dict[error_code]
        except KeyError as e:
            logger.exception(e)
            return {'error_code': None, 'message': 'Неизвестный код ошибки.'}

    @classmethod
    def exception_handler(cls, ex: Exception, object_name: Optional[str] = 'Объект',
                          msg: Optional[str]='Неизвестная ошибка') -> Response:
        """Возвращает DRF Response и логгирует ошибки исходя из переданного исключения."""
        if ex.__class__.__name__ == 'DoesNotExist':
            context = cls.get_err_message(6, object_name)
            logger.error(context)
            logger.exception(ex)
            return Response(context)
        elif ex.__class__.__name__ in ('ParseError', 'DataError'):
            context = cls.get_err_message(3)
            logger.exception(ex)
            logger.info(context)
            return Response(context)
        elif ex.__class__.__name__ == 'ValidationError':
            context = cls.get_err_message(4)
            logger.exception(ex)
            logger.info(context)
            return Response(context)
        elif ex.__class__.__name__ == 'IntegrityError':
            context = cls.get_err_message(5, object_name)
            logger.exception(ex)
            logger.info(context)
            return Response(context) 
        elif ex.__class__.__name__ == 'KeyError':
            context = cls.get_err_message(7)
            logger.exception(ex)
            logger.info(context)
            return Response(context) 
        elif ex.__class__.__name__ == 'TypeError':
            context = cls.get_err_message(8, object_name, msg)
            logger.exception(ex)
            logger.info(context)
            return Response(context)   
        else:
            context = cls.get_err_message(1)
            logger.exception(ex)
            logger.info(context)
            return Response(context)         

