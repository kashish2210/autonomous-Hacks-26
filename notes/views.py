# notes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .models import Claim, NewsReport, VideoGenerationJob
from .forms import ClaimForm, NewsReportForm
from .services.pdf_generator import generate_news_pdf
from .services.veo3_generator import generate_video_with_veo3


@ensure_csrf_cookie
def notes_list(request):
    """Display all claims with search and filter"""
    claims = Claim.objects.filter(is_archived=False)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        claims = claims.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        claims = claims.filter(status=status_filter)
    
    # Filter by language
    language_filter = request.GET.get('language', '')
    if language_filter:
        claims = claims.filter(language=language_filter)
    
    # Pagination
    paginator = Paginator(claims, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'language_filter': language_filter,
        'status_choices': Claim.STATUS_CHOICES,
        'language_choices': Claim.LANGUAGE_CHOICES,
    }
    
    return render(request, 'notes/notes_list.html', context)


@require_http_methods(["GET", "POST"])
def claim_create(request):
    """Create a new claim"""
    if request.method == "POST":
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            if request.user.is_authenticated:
                claim.created_by = request.user
            claim.save()
            
            return JsonResponse({
                'success': True,
                'claim_id': claim.id,
                'message': 'Claim created successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    else:
        form = ClaimForm()
    
    return render(request, 'notes/claim_form.html', {
        'form': form,
        'claim': None
    })


@require_http_methods(["GET", "POST"])
def claim_edit(request, claim_id):
    """Edit an existing claim"""
    claim = get_object_or_404(Claim, id=claim_id)
    
    if request.method == "POST":
        form = ClaimForm(request.POST, instance=claim)
        if form.is_valid():
            claim = form.save(commit=False)
            if request.user.is_authenticated and not claim.created_by:
                claim.created_by = request.user
            claim.save()
            
            return JsonResponse({
                'success': True,
                'claim_id': claim.id,
                'message': 'Claim updated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    else:
        form = ClaimForm(instance=claim)
    
    return render(request, 'notes/claim_form.html', {
        'form': form,
        'claim': claim
    })


@require_http_methods(["POST"])
def claim_delete(request, claim_id):
    """Delete or archive a claim"""
    claim = get_object_or_404(Claim, id=claim_id)
    
    # Archive instead of delete to preserve data
    claim.is_archived = True
    claim.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Claim archived successfully'
    })


@require_http_methods(["POST"])
def bulk_save_claims(request):
    """Save multiple claims from verification pipeline"""
    try:
        data = json.loads(request.body)
        claims_data = data.get('claims', [])
        source_url = data.get('source_url', '')
        source_type = data.get('source_type', 'text')
        
        created_claims = []
        
        for claim_data in claims_data:
            claim = Claim.objects.create(
                title=claim_data.get('title', claim_data.get('claim', ''))[:500],
                content=claim_data.get('claim', ''),
                source_url=source_url,
                source_type=source_type,
                verification_notes=claim_data.get('verification', ''),
                status='pending',
                created_by=request.user if request.user.is_authenticated else None
            )
            created_claims.append({
                'id': claim.id,
                'title': claim.title
            })
        
        return JsonResponse({
            'success': True,
            'created_count': len(created_claims),
            'claims': created_claims
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET", "POST"])
def generate_report(request):
    """Generate PDF or Video report from selected claims"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            claim_ids = data.get('claim_ids', [])
            format_type = data.get('format', 'pdf')
            language = data.get('language', 'en')
            title = data.get('title', 'News Report')
            
            if not claim_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'No claims selected'
                }, status=400)
            
            claims = Claim.objects.filter(id__in=claim_ids)
            
            if not claims.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No valid claims found'
                }, status=404)
            
            # Create report
            report = NewsReport.objects.create(
                title=title,
                format_type=format_type,
                language=language,
                created_by=request.user if request.user.is_authenticated else None
            )
            report.claims.set(claims)
            
            if format_type == 'pdf':
                # Generate PDF
                pdf_file = generate_news_pdf(report)
                report.pdf_file = pdf_file
                report.save()
                
                return JsonResponse({
                    'success': True,
                    'report_id': report.id,
                    'download_url': report.pdf_file.url
                })
                
            elif format_type == 'video':
                # Generate video with Veo 3
                job = VideoGenerationJob.objects.create(
                    report=report,
                    status='pending'
                )
                
                # Start async video generation
                generate_video_with_veo3.delay(report.id, job.id)
                
                return JsonResponse({
                    'success': True,
                    'report_id': report.id,
                    'job_id': job.id,
                    'message': 'Video generation started'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return render(request, 'notes/generate_report.html')


@require_http_methods(["GET"])
def check_video_status(request, job_id):
    """Check status of video generation job"""
    job = get_object_or_404(VideoGenerationJob, id=job_id)
    
    response_data = {
        'status': job.status,
        'created_at': job.created_at.isoformat(),
    }
    
    if job.status == 'completed' and job.report.video_file:
        response_data['download_url'] = job.report.video_file.url
    elif job.status == 'failed':
        response_data['error'] = job.error_message
    
    return JsonResponse(response_data)


@require_http_methods(["GET"])
def download_report(request, report_id):
    """Download generated report"""
    report = get_object_or_404(NewsReport, id=report_id)
    
    if report.format_type == 'pdf' and report.pdf_file:
        return FileResponse(
            report.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"{report.title}.pdf"
        )
    elif report.format_type == 'video' and report.video_file:
        return FileResponse(
            report.video_file.open('rb'),
            as_attachment=True,
            filename=f"{report.title}.mp4"
        )
    
    return JsonResponse({
        'error': 'File not available'
    }, status=404)