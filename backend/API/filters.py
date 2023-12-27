def filterStatus(queryset, request):
    if request.query_params.get('status'):
        return queryset.filter(status=request.query_params.get('status'))
    return queryset

def filtertitle(queryset, request):
    if request.query_params.get('title'):
        return queryset.filter(full_name__startswith = request.query_params.get('title'))
    return queryset

def filterSended(queryset, request):
    start_date = "2020-01-01"
    end_date = "2500-01-01"
    if request.query_params.get('send'):
        return queryset.filter(send__date=request.query_params.get('send'))
    if request.query_params.get('start_date'):
        start_date = request.query_params.get('start_date')
    if request.query_params.get('end_date'):
        end_date = request.query_params.get('end_date')  
    return queryset.filter(send__range=[start_date, end_date])

def filterRequestStatus(queryset, request):
    if request.GET.get('status'):   
        return queryset.filter(status__in=list(request.GET.get('status')))
    return queryset

def filterParticipant(queryset, request):
    return filtertitle(queryset, request)

def filterRequest(queryset, request):
    return filterSended(filterRequestStatus(queryset, request), request)