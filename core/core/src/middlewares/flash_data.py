from django.urls import reverse


class FlashDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        if request.path == reverse('booking:index') and request.method == "GET":
            if 'booking_info_visited' not in request.session:
                request.session['booking_info_visited'] = True
            else:
                request.session.pop('booking_info', None)
                request.session.pop('booking_info_visited')
        if request.path == reverse('booking:index') and request.method == "POST":
            request.session.pop('booking_info', None)
        if request.path != reverse('booking:index') and request.path != reverse('chatbot:diagnose'):
            request.session.pop('booking_info', None)
        return response

    def process_template_response(self, request, response):
        if 'booking_info' in request.session:
            response.context_data['recomanded_doctor_id'] = request.session['booking_info'].get('recomanded_doctor_id')

        return response
