def filterStatus(queryset, request):
    if request.query_params.get('status'):
        return queryset.filter(status=request.query_params.get('status'))
    return queryset

def filterUser(queryset, request):
    if request.query_params.get('user_id'):
        return queryset.filter(user_id=request.query_params.get('user_id'))
    return queryset

def filterModerator(queryset, request):
    if request.query_params.get('moder_id'):
        return queryset.filter(moder_id=request.query_params.get('moder_id'))
    return queryset

def filterParticipant(queryset, request):
    return filterStatus(queryset, request)

def filterRequest(queryset, request):
    return filterModerator(filterUser(filterStatus(queryset, request), request), request)