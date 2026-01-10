from django.shortcuts import render
from django.shortcuts import render
from .forms import ClaimsExtractorForm
# from .claim_extractor.pipeline import run_pipeline
from agents.verifier.pipeline import verifier_run_pipeline

# Create your views here.
def extract_claims(request):
    submitted_text = None

    if request.method == "POST":
        form = ClaimsExtractorForm(request.POST)
        if form.is_valid():
            submitted_text = form.cleaned_data["content"]
            claims = verifier_run_pipeline(submitted_text)

            return render(request, "claim_list.html", {'claims': claims})
    else:
        form = ClaimsExtractorForm()

    return render(request, "extract_claims_form.html", {
        "form": form,
        "submitted_text": submitted_text
    })
