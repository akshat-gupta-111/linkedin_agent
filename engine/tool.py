from engine import parsers, mathematics

def compile_linkedin_payload(raw_data: dict, frontend_config: dict = None) -> dict:
    """
    Ingests scraped LinkedIn data, parses it, and executes the math engine.
    Allows frontend sliders to dynamically alter weights and mathematical constants.
    """
    
    # Establish default parameters if the frontend doesn't provide them
    if not frontend_config:
        frontend_config = {
            "weights": {
                "consistency": 0.20, "engagement": 0.25, 
                "depth": 0.25, "authority": 0.20, "optimization": 0.10
            },
            "constants": {
                "epsilon": 1.0, 
                "comment_weight": 2.0, "repost_weight": 1.5, "reciprocity_bonus": 10.0,
                "alpha": 4.0, "beta": 2.0, "gamma": 1.5,
                "lambda_multiplier": 25.0, "target_features": 5.0
            }
        }

    w = frontend_config["weights"]
    c = frontend_config["constants"]

    # 1. Parse and Clean Data
    bucketed_posts = parsers.bucket_posts_by_month(raw_data.get("recent_posts", []))
    
    # 2. Execute Math Modules
    con_data = mathematics.calculate_consistency_score(
        bucketed_posts, epsilon=c.get("epsilon", 1.0)
    )
    
    eng_data = mathematics.calculate_engagement_score(
        raw_data.get("recent_posts", []), 
        raw_data.get("recommendations", {}),
        comment_weight=c.get("comment_weight", 2.0),
        repost_weight=c.get("repost_weight", 1.5),
        reciprocity_bonus=c.get("reciprocity_bonus", 10.0)
    )
    
    depth_data = mathematics.calculate_depth_score(
        raw_data.get("experience_count", 0),
        raw_data.get("certifications_count", 0),
        raw_data.get("skills", {}),
        alpha=c.get("alpha", 4.0),
        beta=c.get("beta", 2.0),
        gamma=c.get("gamma", 1.5)
    )
    
    auth_data = mathematics.calculate_authority_score(
        raw_data.get("network", {}).get("followers", 0),
        raw_data.get("network", {}).get("connections", 0),
        lambda_multiplier=c.get("lambda_multiplier", 25.0)
    )
    
    opt_data = mathematics.calculate_optimization_score(
        raw_data.get("optimization", {}),
        target_features=c.get("target_features", 5.0)
    )

    # 3. Calculate Final Accumulation
    scores_payload = {
        "consistency": con_data, "engagement": eng_data, 
        "depth": depth_data, "authority": auth_data, "optimization": opt_data
    }
    final_score_data = mathematics.calculate_final_score(scores_payload, w)

    # 4. Construct Final Output Block
    return {
        "user_target": raw_data.get("profile", {}).get("username", "Unknown"),
        "hard_metrics": {
            "final_score": final_score_data["score"],
            "category_scores": {
                "consistency": con_data["score"],
                "engagement": eng_data["score"],
                "depth": depth_data["score"],
                "authority": auth_data["score"],
                "optimization": opt_data["score"]
            },
            "breakdowns": {
                "consistency": con_data["details"],
                "engagement": eng_data["details"],
                "depth": depth_data["details"],
                "authority": auth_data["details"],
                "optimization": opt_data["details"]
            }
        },
        "narrative_context": {
            "top_skills": sorted(raw_data.get("skills", {}).items(), key=lambda item: item[1], reverse=True)[:5],
            "total_experience_roles": raw_data.get("experience_count", 0),
            "total_certifications": raw_data.get("certifications_count", 0)
        }
    }