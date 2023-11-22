def filterStatus(queryset, request):
    if request.query_params.get('status'):
        return queryset.filter(status=request.query_params.get('status'))
    return queryset

def filtertitle(queryset, request):
    if request.query_params.get('title'):
        return queryset.filter(full_name__startswith = request.query_params.get('title'))
    return queryset

def filterCreated(queryset, request):
    lowerdate = "2020-01-01"
    higherdate = "2500-01-01"
    if request.query_params.get('created'):
        return queryset.filter(created__date=request.query_params.get('created'))
    if request.query_params.get('downdate'):
        lowerdate = request.query_params.get('downdate')
    if request.query_params.get('update'):
        higherdate = request.query_params.get('update')
    return queryset.filter(created__range=[lowerdate, higherdate])

def filterParticipant(queryset, request):
    return filtertitle(filterStatus(queryset, request), request)

def filterRequest(queryset, request):
    return filterCreated(filterStatus(queryset, request), request)