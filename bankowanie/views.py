from django.shortcuts import render, HttpResponse

# main paige, both logged and not logged as well
def main(request):
    return HttpResponse("na razie pusto")
    #return render(request)

    