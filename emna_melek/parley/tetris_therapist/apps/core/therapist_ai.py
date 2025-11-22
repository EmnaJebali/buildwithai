"""
Tetris Therapist AI - Generates savage, hilarious roasts based on player stats.
"""
import random


class TetrisTherapist:
    """A brutally honest AI therapist that roasts your Tetris skills."""
    
    def __init__(self):
        self.roast_templates = {
            'rotation_abuse': [
                "You rotate {count} times per piece. Commitment issues much?",
                "{count} rotations per piece? Can't make up your mind, can you?",
                "Rotating {count} times per piece is like asking for directions {count} times and still getting lost.",
                "Your rotation count ({count}) suggests you're more indecisive than a weather forecast.",
                "{count} rotations? At this point, you're just spinning in circles. Literally.",
            ],
            'no_rotations': [
                "Zero rotations? You play Tetris like you're afraid of change.",
                "Not a single rotation? Your piece is stuck in one position, just like your life choices.",
                "You never rotate. This is the Tetris equivalent of eating the same sandwich every day.",
                "Zero rotations detected. Your pieces are more rigid than your personality.",
            ],
            'hold_never_used': [
                "Never used hold? Afraid of second chances?",
                "Hold button exists, you know. It's like having a backup plan but you're too proud to use it.",
                "Zero holds. You commit to bad decisions like you're running for office.",
                "You've never held a piece. This explains why you can't hold a conversation either.",
            ],
            'hold_abuse': [
                "You hold {count} times per piece. Can't commit to anything, can you?",
                "{count} holds? You're treating pieces like dating apps - swipe left, swipe right, never settle.",
                "Holding {count} times per piece is like changing your mind {count} times in a conversation.",
            ],
            'hard_drop_abuse': [
                "You hard drop {count} times. Impatient much? Can't wait 2 seconds?",
                "{count} hard drops? You're the Tetris equivalent of someone who skips to the end of movies.",
                "Hard dropping {count} times is like always taking the express lane because you can't handle the journey.",
            ],
            'no_hard_drops': [
                "Never hard dropped? You're playing Tetris like you're reading terms and conditions - slowly and carefully.",
                "Zero hard drops. You take your time, I'll give you that. Too much time.",
            ],
            'low_tetris_rate': [
                "Only {count} Tetrises? You clear lines like you clear your browser history - one at a time, shamefully.",
                "{count} Tetrises with {pieces} pieces? That's a {rate}% rate. My grandmother gets better Tetris rates, and she's dead.",
                "Your Tetris rate is {rate}%. At this point, you're just clearing lines to survive, not to excel.",
            ],
            'high_tetris_rate': [
                "Okay, {rate}% Tetris rate is actually impressive. But your personality is still {rate}% terrible.",
                "{rate}% Tetris rate? Great! Now work on your {other_stat} problem.",
            ],
            'low_score': [
                "Score of {score}? That's not a score, that's a cry for help.",
                "{score} points? I've seen higher scores in participation trophies.",
                "Your score ({score}) is lower than my expectations, and those were already in the basement.",
            ],
            'many_pieces_no_progress': [
                "{pieces} pieces and only {lines} lines? You're building a wall, not playing Tetris.",
                "{pieces} pieces, {lines} lines. Your efficiency is lower than a broken calculator.",
            ],
            'general_roasts': [
                "Your gameplay is like your life - chaotic, directionless, and ultimately disappointing.",
                "I've seen better Tetris skills in a broken Game Boy from 1989.",
                "You play Tetris like you're trying to fail. And you're succeeding!",
                "Your strategy is as clear as your future prospects.",
                "I diagnose you with: bad at Tetris. The treatment? Stop playing.",
                "You're not playing Tetris, you're committing Tetris crimes.",
                "Your board looks like a Rorschach test, and the answer is always 'failure'.",
            ],
        }
    
    def generate_roast(self, stats, score, lines_cleared, level, action_type=None, recent_stats=None, used_roasts=None):
        """Generate a contextual roast based on player statistics and recent action."""
        if used_roasts is None:
            used_roasts = []
        pieces_placed = stats.get('total_pieces', 1)
        rotations = stats.get('total_rotations', 0)
        holds = stats.get('hold_uses', 0)
        hard_drops = stats.get('hard_drops', 0)
        tetris_count = stats.get('tetris_count', 0)
        soft_drops = stats.get('soft_drops', 0)
        
        # Calculate rates
        rotations_per_piece = rotations / pieces_placed if pieces_placed > 0 else 0
        holds_per_piece = holds / pieces_placed if pieces_placed > 0 else 0
        hard_drops_per_piece = hard_drops / pieces_placed if pieces_placed > 0 else 0
        tetris_rate = (tetris_count / pieces_placed * 100) if pieces_placed > 0 else 0
        
        # Contextual roasts based on recent action
        roasts = []
        
        # Action-specific contextual roasts
        if action_type:
            if action_type == 'rotate':
                recent_rots = recent_stats.get('recent_rotations', 0) if recent_stats else 0
                if recent_rots > 3:
                    roasts.append(f"Still rotating? You've rotated this piece {recent_rots} times. Make a decision already!")
                elif rotations_per_piece > 4:
                    roasts.append(f"You just rotated. That's {round(rotations_per_piece, 1)} rotations per piece on average. Indecisive much?")
                elif rotations_per_piece > 2:
                    roasts.append("Another rotation? Can't decide which way to face? Classic.")
                else:
                    roasts.append("Rotating the piece? Good, at least you're trying different angles.")
            
            elif action_type == 'hard_drop':
                if hard_drops_per_piece > 0.7:
                    roasts.append("Hard dropping again? You're so impatient, you probably skip to the end of movies.")
                else:
                    roasts.append("Hard drop? Can't wait for gravity to do its job? Classic impatience.")
            
            elif action_type == 'hold':
                if holds == 0:
                    roasts.append("First time using hold? Finally decided to give second chances a try?")
                elif holds_per_piece > 0.4:
                    roasts.append("Holding again? You're treating pieces like dating apps - swipe left, never commit.")
                else:
                    roasts.append("Using hold? Good. At least you're learning to plan ahead. Barely.")
            
            elif action_type == 'move_left':
                recent_moves = recent_stats.get('recent_moves', 0) if recent_stats else 0
                if recent_moves > 5:
                    roasts.append(f"Moving left again? You've been going back and forth {recent_moves} times. Can't decide where to put it?")
                elif recent_moves > 3:
                    roasts.append("Moving left? After all that right movement? Make up your mind!")
                else:
                    roasts.append("Moving left? Good positioning.")
            
            elif action_type == 'move_right':
                recent_moves = recent_stats.get('recent_moves', 0) if recent_stats else 0
                if recent_moves > 5:
                    roasts.append(f"Moving right now? After all that left movement? You've moved {recent_moves} times. Pick a side!")
                elif recent_moves > 3:
                    roasts.append("Moving right? Can't decide? This is peak indecision.")
                else:
                    roasts.append("Moving right? Positioning looks good.")
            
            elif action_type == 'move_down' or action_type == 'soft_drop':
                if soft_drops > pieces_placed * 0.8:
                    roasts.append("Soft dropping again? You're in such a hurry, but not enough to hard drop. Confusing.")
                else:
                    roasts.append("Taking your time? Unusual for you.")
        
        # Priority-based roasting (most savage first)
        
        # Rotation abuse (very common)
        if rotations_per_piece > 3:
            roasts.append(random.choice(self.roast_templates['rotation_abuse']).format(
                count=round(rotations_per_piece, 1)
            ))
        elif rotations_per_piece == 0 and pieces_placed > 5:
            roasts.append(random.choice(self.roast_templates['no_rotations']))
        
        # Hold usage
        if holds == 0 and pieces_placed > 10:
            roasts.append(random.choice(self.roast_templates['hold_never_used']))
        elif holds_per_piece > 0.5:
            roasts.append(random.choice(self.roast_templates['hold_abuse']).format(
                count=round(holds_per_piece, 1)
            ))
        
        # Hard drop usage
        if hard_drops == 0 and pieces_placed > 10:
            roasts.append(random.choice(self.roast_templates['no_hard_drops']))
        elif hard_drops_per_piece > 0.8:
            roasts.append(random.choice(self.roast_templates['hard_drop_abuse']).format(
                count=round(hard_drops_per_piece, 1)
            ))
        
        # Tetris rate
        if pieces_placed > 20:
            if tetris_rate < 5:
                roasts.append(random.choice(self.roast_templates['low_tetris_rate']).format(
                    count=tetris_count,
                    pieces=pieces_placed,
                    rate=round(tetris_rate, 1)
                ))
            elif tetris_rate > 20:
                # Find another stat to roast
                other_stat = "rotation" if rotations_per_piece > 2 else "commitment"
                roasts.append(random.choice(self.roast_templates['high_tetris_rate']).format(
                    rate=round(tetris_rate, 1),
                    other_stat=other_stat
                ))
        
        # Score-based roasts
        if score < 1000 and pieces_placed > 15:
            roasts.append(random.choice(self.roast_templates['low_score']).format(score=score))
        
        # Efficiency roasts
        if pieces_placed > 20 and lines_cleared < pieces_placed / 3:
            roasts.append(random.choice(self.roast_templates['many_pieces_no_progress']).format(
                pieces=pieces_placed,
                lines=lines_cleared
            ))
        
        # Filter out used roasts
        available_roasts = [r for r in roasts if r not in used_roasts]
        
        # If no unique roasts available, reset and use all roasts (but still try to avoid recent ones)
        if not available_roasts:
            available_roasts = roasts
            # If still no roasts, get general ones
            if not available_roasts:
                all_general = self.roast_templates['general_roasts']
                available_general = [r for r in all_general if r not in used_roasts[-20:]]  # Avoid last 20
                if available_general:
                    available_roasts = available_general
                else:
                    available_roasts = all_general  # If all used, reset
        
        # If we have action-specific roasts, prioritize them
        if action_type and len(available_roasts) > 0:
            # Return a random action-specific roast (they're more contextual)
            return random.choice(available_roasts[:5]) if len(available_roasts) > 5 else random.choice(available_roasts)
        
        # Return a random available roast
        return random.choice(available_roasts) if available_roasts else random.choice(roasts)
    
    def generate_line_clear_roast(self, lines_cleared, score, level):
        """Generate a backhanded compliment when lines are cleared."""
        backhanded_compliments = {
            1: [
                "One line? Well, at least you're trying. I guess.",
                "One line cleared. Baby steps, I suppose.",
                "A single line? Congratulations on the bare minimum.",
                "One line down. Only took you forever to get there.",
                "One line cleared. I've seen better, but I've also seen worse. Barely."
            ],
            2: [
                "Two lines? Not bad. For a beginner. In 1990.",
                "Double line clear. You're getting there. Slowly.",
                "Two lines? That's... acceptable. I guess.",
                "Double clear. At least you're not completely hopeless.",
                "Two lines. Progress, I suppose. If you can call it that."
            ],
            3: [
                "Three lines? That's actually decent. For once.",
                "Triple line clear. Not terrible. For you.",
                "Three lines? I'm almost impressed. Almost.",
                "Triple clear. You're getting better. Marginally.",
                "Three lines. That's... actually not bad. Shocking."
            ],
            4: [
                "Tetris! Four lines! Now that's actually impressive. Too bad it took you this long.",
                "Tetris! Well done! For once, you did something right.",
                "Four lines cleared! I'm genuinely surprised. Good job. I guess.",
                "Tetris! That was actually good. Don't let it go to your head.",
                "Four lines! Finally, some actual skill. Keep it up. If you can."
            ]
        }
        
        if lines_cleared in backhanded_compliments:
            return random.choice(backhanded_compliments[lines_cleared])
        else:
            return f"{lines_cleared} lines cleared. That's... something."
    
    def generate_final_report(self, stats, score, lines_cleared, level, game_duration=None):
        """Generate a final therapy report after game over."""
        pieces_placed = stats.get('total_pieces', 0)
        rotations = stats.get('total_rotations', 0)
        holds = stats.get('hold_uses', 0)
        hard_drops = stats.get('hard_drops', 0)
        tetris_count = stats.get('tetris_count', 0)
        
        # Calculate metrics
        rotations_per_piece = rotations / pieces_placed if pieces_placed > 0 else 0
        tetris_rate = (tetris_count / pieces_placed * 100) if pieces_placed > 0 else 0
        
        report = {
            'score': score,
            'lines_cleared': lines_cleared,
            'level_reached': level,
            'pieces_placed': pieces_placed,
            'rotations_per_piece': round(rotations_per_piece, 2),
            'hold_uses': holds,
            'hard_drops': hard_drops,
            'tetris_count': tetris_count,
            'tetris_rate': round(tetris_rate, 1),
        }
        
        # Generate summary roast
        summary_parts = []
        
        if rotations_per_piece > 3:
            summary_parts.append(f"Indecisive (rotated {rotations_per_piece:.1f}x per piece)")
        if holds == 0 and pieces_placed > 10:
            summary_parts.append("Commitment-phobic (never used hold)")
        if tetris_rate < 5 and pieces_placed > 20:
            summary_parts.append(f"Tetris-deficient ({tetris_rate:.1f}% Tetris rate)")
        if score < 1000:
            summary_parts.append("Low-scoring")
        
        if not summary_parts:
            summary_parts.append("Mediocre")
        
        report['diagnosis'] = ", ".join(summary_parts)
        report['final_roast'] = self.generate_roast(stats, score, lines_cleared, level)
        
        return report

