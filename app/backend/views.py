from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post, get
from rest_framework import status
from rest_framework.response import Response
from .util import update_or_create_user, is_spotify_authenticated, get_user, log_out

# Create your views here.

class AuthURL(APIView):
    def get(self, request, fornat=None):
        scopes = 'playlist-modify-public playlist-modify-private user-library-read playlist-read-private'

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')


    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(
            request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

class LogOut(APIView):
    def get(self, request, format=None):
        logout_status = log_out(
            request.session.session_key)
        return Response({'status': logout_status}, status=status.HTTP_200_OK)


class UserInfo(APIView):
    def get(self, request, format=None):
        pic_url = 'None'
        pred_count = 0
        name = 'None'
        user = get_user(session_key=request.session.session_key)
        if user:
            pic_url = user.pic_url
            pred_count = user.pred_count
            name = user.uid

        return Response({'img': pic_url,
                         'predCount': pred_count,
                         'name': name},
                          status=status.HTTP_200_OK)