class FlashDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        flash_data = request.session.pop('_flash_data', None)  # Retrieve the flash data from the session
        request.session['_flash_data'] = flash_data  # Store the flash data in a separate session key

        response = self.get_response(request)

        if '_flash_data' in request.session:  # If flash data was set during the request
            del request.session['_flash_data']  # Delete the temporary flash data key

        return response
