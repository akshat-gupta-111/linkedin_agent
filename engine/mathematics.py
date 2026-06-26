import math

def calculate_consistency_score(monthly_buckets: dict, epsilon: float = 1.0) -> dict:
    """Calculates the consistency score using Log-Dampened Coefficient of Variation."""
    if not monthly_buckets:
        # FIX: Added epsilon to early return
        return {"score": 0.0, "details": {"mu": 0.0, "sigma": 0.0, "total_posts": 0, "epsilon": epsilon}}

    posts = list(monthly_buckets.values())
    total_months = len(posts)
    raw_total_posts = sum(posts)
    
    if raw_total_posts == 0:
        # FIX: Added epsilon to early return
        return {"score": 0.0, "details": {"mu": 0.0, "sigma": 0.0, "total_posts": 0, "epsilon": epsilon}}

    log_posts = [math.log2(p + 1) for p in posts]
    log_mu = sum(log_posts) / total_months
    variance = sum((p - log_mu) ** 2 for p in log_posts) / total_months
    log_sigma = math.sqrt(variance)

    score = max(0.0, 100.0 * (1.0 - (log_sigma / (log_mu + epsilon))))

    return {
        "score": round(min(100.0, score), 2),
        "details": {"mu": round(log_mu, 2), "sigma": round(log_sigma, 2), "total_posts": raw_total_posts, "epsilon": epsilon}
    }


def calculate_engagement_score(posts: list, recommendations: dict, comment_weight: float = 2.0, repost_weight: float = 1.5, reciprocity_bonus: float = 10.0) -> dict:
    """Calculates engagement depth by weighting comments and shares over raw likes."""
    if not posts:
        return {"score": 0.0, "details": {"avg_depth": 0.0, "reciprocity": 0.0}}

    total_depth = 0.0
    for post in posts:
        likes = post.get("likes", 0)
        comments = post.get("comments", 0)
        reposts = post.get("reposts", 0)
        
        post_value = ((comments * comment_weight) + (reposts * repost_weight)) / (likes + 1)
        total_depth += post_value
        
    avg_depth = total_depth / len(posts)
    
    recs_given = recommendations.get("given", 0)
    recs_received = recommendations.get("received", 0)
    reciprocity = min(recs_given, recs_received) * reciprocity_bonus
    
    score = (avg_depth * 100) + reciprocity
    return {
        "score": round(min(100.0, score), 2),
        "details": {"avg_depth": round(avg_depth, 3), "reciprocity": reciprocity}
    }


def calculate_depth_score(experience: int, certs: int, skills: dict, alpha: float = 4.0, beta: float = 2.0, gamma: float = 1.5) -> dict:
    """Calculates professional depth balancing roles, certs, and skill endorsements."""
    log_endorsements_sum = sum(math.log2(count + 1) for count in skills.values())
    
    score = (experience * alpha) + (certs * beta) + (log_endorsements_sum * gamma)
    
    return {
        "score": round(min(100.0, score), 2),
        "details": {"experience_points": experience * alpha, "cert_points": certs * beta, "skill_points": round(log_endorsements_sum * gamma, 2)}
    }


def calculate_authority_score(followers: int, connections: int, lambda_multiplier: float = 25.0) -> dict:
    """Calculates network reach using a Base-10 Logarithm to normalize massive audiences."""
    audience_size = followers + connections
    if audience_size <= 0:
        # FIX: Added lambda to early return
        return {"score": 0.0, "details": {"audience": 0, "lambda": lambda_multiplier}}
        
    score = math.log10(audience_size + 1) * lambda_multiplier
    
    return {
        "score": round(min(100.0, score), 2),
        "details": {"audience": audience_size, "lambda": lambda_multiplier}
    }


def calculate_optimization_score(flags: dict, target_features: float = 5.0) -> dict:
    """Calculates a simple percentage based on utilized profile features."""
    if not flags:
        # FIX: Added target_features to early return to prevent UI crash
        return {"score": 0.0, "details": {"active_features": 0, "target_features": target_features}}
        
    active_features = sum(1 for value in flags.values() if value is True)
    score = (active_features / target_features) * 100.0
    
    return {
        "score": round(min(100.0, score), 2),
        "details": {"active_features": active_features, "target_features": target_features}
    }


def calculate_final_score(scores: dict, weights: dict) -> dict:
    """Generates the final weighted score based on frontend slider weights."""
    final_score = 0.0
    for category, module_data in scores.items():
        weight = float(weights.get(category, 0.0))
        final_score += module_data["score"] * weight
        
    return {
        "score": round(final_score, 2),
        "details": {"applied_weights": weights}
    }