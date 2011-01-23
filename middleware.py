# This set the user in a static property of a UserInfo class
class GlobalUser:
    
    user = False
    
    def process_request(self, request):
        GlobalUser.user = request.user