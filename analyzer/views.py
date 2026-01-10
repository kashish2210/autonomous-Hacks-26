from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Article
from .agents import AdvancedSourceAnalyzer
from .scraper import ArticleScraper
import json
import time
from dotenv import load_dotenv

load_dotenv()

def index(request):
    """Analyzer main page with split-screen layout"""
    recent_analyses = Article.objects.all()[:10]
    return render(request, 'analyzer.html', {
        'recent_analyses': recent_analyses
    })

def analyze_article_stream(request):
    """Stream analysis progress in real-time with advanced agents"""
    if request.method == 'POST':
        article_url = request.POST.get('article_url', '')
        
        def event_stream():
            try:
                # Step 1: Scraping
                yield f"data: {json.dumps({'step': 'scraping', 'message': 'Initializing web scraper...', 'agent': 'Web Scraper'})}\n\n"
                time.sleep(0.3)
                
                scraper = ArticleScraper()
                yield f"data: {json.dumps({'step': 'scraping', 'message': f'Fetching content from {article_url}', 'agent': 'Web Scraper'})}\n\n"
                
                scraped_data = scraper.scrape_article(article_url)
                
                if not scraped_data['success']:
                    yield f"data: {json.dumps({'step': 'error', 'message': scraped_data['error']})}\n\n"
                    return
                
                yield f"data: {json.dumps({'step': 'scraping', 'message': 'Content extracted successfully', 'agent': 'Web Scraper', 'progress': 15})}\n\n"
                time.sleep(0.3)
                
                # Step 2: Initialize advanced agent system
                yield f"data: {json.dumps({'step': 'init', 'message': 'Initializing LangChain multi-agent system...', 'agent': 'System', 'progress': 20})}\n\n"
                analyzer = AdvancedSourceAnalyzer()
                time.sleep(0.3)
                
                article_text = scraped_data['content']
                
                # Step 3: Deep Source Extraction
                yield f"data: {json.dumps({'step': 'agent1', 'message': 'Performing deep source extraction with credibility analysis...', 'agent': 'Agent 1: Deep Source Extractor', 'progress': 30})}\n\n"
                time.sleep(0.5)
                yield f"data: {json.dumps({'step': 'agent1', 'message': 'Analyzing source credentials and expertise relevance...', 'agent': 'Agent 1: Deep Source Extractor', 'progress': 35})}\n\n"
                time.sleep(0.5)
                
                # Step 4: Anonymous Attribution Analysis
                yield f"data: {json.dumps({'step': 'agent2', 'message': 'Hunting anonymous attributions with vagueness scoring...', 'agent': 'Agent 2: Anonymous Hunter', 'progress': 45})}\n\n"
                time.sleep(0.5)
                yield f"data: {json.dumps({'step': 'agent2', 'message': 'Calculating vagueness scores for each phrase...', 'agent': 'Agent 2: Anonymous Hunter', 'progress': 50})}\n\n"
                time.sleep(0.5)
                
                # Step 5: Bias Detection
                yield f"data: {json.dumps({'step': 'agent3', 'message': 'Detecting selection, framing, and language bias...', 'agent': 'Agent 3: Bias Detector', 'progress': 60})}\n\n"
                time.sleep(0.5)
                yield f"data: {json.dumps({'step': 'agent3', 'message': 'Analyzing source bias and omission patterns...', 'agent': 'Agent 3: Bias Detector', 'progress': 65})}\n\n"
                time.sleep(0.5)
                
                # Step 6: Red Flag Identification
                yield f"data: {json.dumps({'step': 'agent4', 'message': 'Identifying journalism red flags with severity levels...', 'agent': 'Agent 4: Red Flag Auditor', 'progress': 75})}\n\n"
                time.sleep(0.5)
                
                # Step 7: Quality Metrics
                yield f"data: {json.dumps({'step': 'agent5', 'message': 'Calculating diversity, authority, independence scores...', 'agent': 'Agent 5: Quality Calculator', 'progress': 85})}\n\n"
                time.sleep(0.5)
                yield f"data: {json.dumps({'step': 'agent5', 'message': 'Computing final transparency score with strict criteria...', 'agent': 'Agent 5: Quality Calculator', 'progress': 90})}\n\n"
                time.sleep(0.5)
                
                # Step 8: Generate Recommendations
                yield f"data: {json.dumps({'step': 'agent6', 'message': 'Generating actionable improvement recommendations...', 'agent': 'Agent 6: Recommendation Engine', 'progress': 95})}\n\n"
                time.sleep(0.5)
                
                # Run the complete analysis
                results = analyzer.analyze_article(article_text, {
                    'title': scraped_data.get('title', 'Untitled'),
                    'url': article_url
                })
                
                # Determine score interpretation
                transparency_score = results['transparency_score']
                if transparency_score >= 80:
                    score_verdict = "Excellent - High transparency with strong sourcing"
                elif transparency_score >= 60:
                    score_verdict = "Good - Adequate transparency with some concerns"
                elif transparency_score >= 40:
                    score_verdict = "Fair - Limited transparency, multiple issues"
                elif transparency_score >= 20:
                    score_verdict = "Poor - Weak sourcing and low transparency"
                else:
                    score_verdict = "Critical - Severe transparency issues"
                
                yield f"data: {json.dumps({'step': 'agent6', 'message': f'Score: {transparency_score}/100 - {score_verdict}', 'agent': 'Agent 6: Recommendation Engine', 'progress': 98})}\n\n"
                time.sleep(0.3)
                
                # Save to database
                article = Article.objects.create(
                    title=scraped_data.get('title', 'Untitled'),
                    content=article_text,
                    url=article_url,
                    named_sources=results['named_sources'],
                    anonymous_phrases=results['anonymous_phrases'],
                    unique_source_count=results['unique_source_count'],
                    transparency_score=transparency_score,
                    red_flags=results['red_flags'],
                    source_breakdown=results['source_breakdown'],
                    attribution_patterns={
                        'bias_analysis': results['bias_analysis'],
                        'source_quality': results['source_quality'],
                        'recommendations': results['improvement_recommendations']
                    }
                )
                
                yield f"data: {json.dumps({'step': 'complete', 'message': 'Advanced analysis complete!', 'agent': 'System', 'progress': 100, 'article_id': article.id, 'score': transparency_score})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"
        
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def results(request, article_id):
    """Display analysis results"""
    article = get_object_or_404(Article, id=article_id)
    
    score = article.transparency_score
    if score >= 70:
        score_color = 'success'
        score_label = 'Excellent'
    elif score >= 40:
        score_color = 'warning'
        score_label = 'Moderate'
    else:
        score_color = 'danger'
        score_label = 'Poor'
    
    return render(request, 'results.html', {
        'article': article,
        'score_color': score_color,
        'score_label': score_label
    })