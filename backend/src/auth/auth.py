import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'coffee-shop-conjohn712.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

# REFERENCE FOR THIS WHOLE FILE: https://github.com/udacity/FSND/blob/master/BasicFlaskAuth/app.py

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    """ Obtains the Access Token from the Authorization Header """

    # Request authorization credentials. 401 Error if not found
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected'
        }, 401)

    # Split authorization header into parts
    parts = auth.split()

    #If the first part is not 'bearer', raise a 401 error (Great rhyme)
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header', 
            "description": 'Authorization header must start with "Bearer".'
        }, 401)
    
    # If the length of parts is 1, raise a 401 error
    elif len(parts) == 1: 
        raise AuthError({
            'code': 'invalid_header', 
            'description': 'Token not found.'
        }, 401)

    # If the length of parts is greater than 2, raise a 401 error
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    # Set 'token' variable = the second item in parts, return token
    token = parts[1]
    return token


# Reference: 'Access and Authorization': Lesson 4: 'Using RBAC in Flask'
def check_permissions(permission, payload):
    """ 
    A function that searches through the permissions to ensure 
    the right authorization permissions are present. 
    """

    # If string 'permissions' not found, return 400 error
    if 'permissions' not in payload: 
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    # If the user doesn't have permission, raise unauthorized error
    # an unauthorized error
    if permission not in payload['permissions']: 
        raise AuthError({
            'code': 'unauthorized', 
            'description': 'Permission not found.'
        }, 403)
    
    # If permission is in payload and user's list, return true
    return True


def verify_decode_jwt(token):
    """ A function that takes the JWT token and decodes it into JSON """

    # Uses provided url to retrieve JSON url key
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Retrieves unverified header
    unverified_header = jwt.get_unverified_header(token)

    # Sets a blank instantiation of rsa_key
    rsa_key = {}

    # If 'kid' isn't a verified header, raise 401 error
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # Loop through keys, if key 'kid' matches unverified header, 
    # fill rsa_key with other keys
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # If rsa_key not empty, decode the payload and return        
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        # Set an exception to stop decoding of expired tokens
        # Raise 401 error if token expired
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        # Raise 401 error if URL information is inaccurate
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        # Raise 400 error if token cannot be parsed
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    # Raise 400 error if the right key is not found
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator