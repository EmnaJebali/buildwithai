"""
Django views for Tetris Therapist game.
"""
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .tetris_engine import TetrisEngine
from .therapist_ai import TetrisTherapist


def index(request):
    """Landing page."""
    return render(request, 'index.html')


def game(request):
    """Main game page."""
    return render(request, 'game.html')


@require_http_methods(["POST"])
def start_game(request):
    """Initialize a new game."""
    engine = TetrisEngine()
    therapist = TetrisTherapist()
    
    # Store in session
    request.session['game_state'] = engine.get_state()
    request.session['therapist_last_roast_time'] = 0
    request.session['game_start_time'] = None
    # Reset used roasts when starting a new game
    request.session['therapist_used_roasts'] = []
    
    return JsonResponse({
        'success': True,
        'game_state': engine.get_state()
    })


@require_http_methods(["POST"])
def get_state(request):
    """Get current game state."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    return JsonResponse({
        'success': True,
        'game_state': engine.get_state()
    })


@require_http_methods(["POST"])
def move_left(request):
    """Move piece left."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.move_left()
    request.session['game_state'] = engine.get_state()
    
    return _get_game_response(engine, request)


@require_http_methods(["POST"])
def move_right(request):
    """Move piece right."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.move_right()
    request.session['game_state'] = engine.get_state()
    
    return _get_game_response(engine, request)


@require_http_methods(["POST"])
def move_down(request):
    """Move piece down (soft drop)."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    landed = not engine.move_down()
    request.session['game_state'] = engine.get_state()
    
    response = _get_game_response(engine, request)
    response['landed'] = landed
    return response


@require_http_methods(["POST"])
def hard_drop(request):
    """Hard drop piece."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.hard_drop()
    request.session['game_state'] = engine.get_state()
    
    return _get_game_response(engine, request)


@require_http_methods(["POST"])
def rotate(request):
    """Rotate piece."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.rotate()
    request.session['game_state'] = engine.get_state()
    
    return _get_game_response(engine, request)


@require_http_methods(["POST"])
def hold(request):
    """Hold current piece."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.hold()
    request.session['game_state'] = engine.get_state()
    
    return _get_game_response(engine, request)


@require_http_methods(["POST"])
def toggle_pause(request):
    """Toggle pause state."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    engine.toggle_pause()
    request.session['game_state'] = engine.get_state()
    
    return JsonResponse({
        'success': True,
        'paused': engine.paused,
        'game_state': engine.get_state()
    })


@require_http_methods(["POST"])
def get_therapist_roast(request):
    """Get a therapist roast (called periodically or after actions)."""
    import json
    
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    if game_state.get('game_over'):
        return JsonResponse({'roast': None})
    
    # Get action context from request body if provided
    action_type = None
    recent_stats = None
    try:
        body = json.loads(request.body)
        action_type = body.get('action_type')
        recent_stats = body.get('recent_stats')
    except:
        pass
    
    # Get list of used roasts to avoid repeats
    used_roasts = request.session.get('therapist_used_roasts', [])
    
    engine = TetrisEngine(game_state)
    therapist = TetrisTherapist()
    
    # Try to generate a unique roast (max 10 attempts to avoid infinite loop)
    roast = None
    for attempt in range(10):
        roast = therapist.generate_roast(
            engine.stats,
            engine.score,
            engine.lines_cleared,
            engine.level,
            action_type=action_type,
            recent_stats=recent_stats,
            used_roasts=used_roasts
        )
        
        # If roast is unique, break
        if roast not in used_roasts:
            break
    
    # Add to used roasts list (keep last 50 to avoid memory issues)
    if roast:
        used_roasts.append(roast)
        if len(used_roasts) > 50:
            used_roasts = used_roasts[-50:]  # Keep last 50
        request.session['therapist_used_roasts'] = used_roasts
    
    return JsonResponse({
        'roast': roast,
        'show': True
    })


@require_http_methods(["POST"])
def get_final_report(request):
    """Get final therapy report after game over."""
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    engine = TetrisEngine(game_state)
    therapist = TetrisTherapist()
    
    report = therapist.generate_final_report(
        engine.stats,
        engine.score,
        engine.lines_cleared,
        engine.level
    )
    
    return JsonResponse({
        'success': True,
        'report': report
    })


def _get_game_response(engine, request, action_type=None):
    """Helper to generate standard game response with optional therapist roast."""
    # Check if lines were just cleared and trigger backhanded compliment
    roast = None
    if engine.stats.get('last_lines_cleared', 0) > 0:
        lines_cleared = engine.stats['last_lines_cleared']
        therapist = TetrisTherapist()
        roast = therapist.generate_line_clear_roast(lines_cleared, engine.score, engine.level)
        # Reset the flag
        engine.stats['last_lines_cleared'] = 0
        request.session['game_state'] = engine.get_state()
    
    response = {
        'success': True,
        'game_state': engine.get_state(),
        'roast': roast
    }
    
    return JsonResponse(response)

