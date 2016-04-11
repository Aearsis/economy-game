class TeamMiddleware(object):
    def process_request(self, request):
        if hasattr(request.user, 'player'):
            request.team = request.user.player.team
