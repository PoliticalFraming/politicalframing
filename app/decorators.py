# from datetime import timedelta
# from functools import wraps, update_wrapper
# from flask import Flask, make_response, request, current_app

# # Generic HTTP headers decorator
# # http://flask.pocoo.org/snippets/100/

# # Example: @add_response_headers({'X-Robots-Tag': 'noindex'})
# def add_response_headers(headers={}):
#     """This decorator adds the headers passed in to the response"""
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             resp = make_response(f(*args, **kwargs))
#             h = resp.headers
#             for header, value in headers.items():
#                 h[header] = value
#             return resp
#         return decorated_function
#     return decorator

# def noindex(f):
#     """This decorator passes X-Robots-Tag: noindex"""
#     @wraps(f)
#     @add_response_headers({'X-Robots-Tag': 'noindex'})
#     def decorated_function(*args, **kwargs):
#         return f(*args, **kwargs)
#     return decorated_function


# # Decorator for the HTTP Access Control
# # http://flask.pocoo.org/snippets/56/

# # Example: @crossdomain(origin='*')
# def crossdomain(origin=None, methods=None, headers=None,
#                 max_age=21600, attach_to_all=True,
#                 automatic_options=True):
#     if methods is not None:
#         methods = ', '.join(sorted(x.upper() for x in methods))
#     if headers is not None and not isinstance(headers, basestring):
#         headers = ', '.join(x.upper() for x in headers)
#     if not isinstance(origin, basestring):
#         origin = ', '.join(origin)
#     if isinstance(max_age, timedelta):
#         max_age = max_age.total_seconds()

#     def get_methods():
#         if methods is not None:
#             return methods

#         options_resp = current_app.make_default_options_response()
#         return options_resp.headers['allow']

#     def decorator(f):
#         def wrapped_function(*args, **kwargs):
#             if automatic_options and request.method == 'OPTIONS':
#                 resp = current_app.make_default_options_response()
#             else:
#                 resp = make_response(f(*args, **kwargs))
#             if not attach_to_all and request.method != 'OPTIONS':
#                 return resp

#             h = resp.headers

#             h['Access-Control-Allow-Origin'] = origin
#             h['Access-Control-Allow-Credentials'] = 'true' # added by Al
#             h['Access-Control-Allow-Methods'] = get_methods()
#             h['Access-Control-Max-Age'] = str(max_age)
#             if headers is not None:
#                 h['Access-Control-Allow-Headers'] = headers
#             return resp

#         f.provide_automatic_options = False
#         f.required_methods = ['OPTIONS'] # added by Al as per comment
#         return update_wrapper(wrapped_function, f)
#     return decorator


