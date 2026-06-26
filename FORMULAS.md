# 🧮 LinkGent: Mathematical Scoring Architecture

This document outlines the deterministic mathematical formulas used by the **LinkGent** scoring engine. By decoupling the telemetry extraction from the scoring logic, this engine provides an objective, highly tunable evaluation of a professional's LinkedIn footprint.

---

## ⚖️ Default Weights & Constants
The engine relies on a set of weights and constants that can be dynamically altered via the UI. Below are the values for the **Default (Balanced Assessor)** persona.

**Category Weights:**
* Consistency ($W_{cons}$): 20%
* Engagement ($W_{eng}$): 25%
* Depth ($W_{dep}$): 25%
* Authority ($W_{auth}$): 20%
* Optimization ($W_{opt}$): 10%

**Mathematical Constants:**
* $\epsilon$ (Epsilon / Forgiveness): `1.0`
* $C_{w}$ (Comment Weight): `2.0`
* $R_{w}$ (Repost Weight): `1.5`
* $R_{bonus}$ (Reciprocity Bonus): `10.0`
* $\alpha$ (Experience Points): `4.0`
* $\beta$ (Certification Points): `2.0`
* $\gamma$ (Skill Log-Multiplier): `1.5`
* $\lambda$ (Audience Log-Scale): `25.0`
* $F_{target}$ (Target Features): `5.0`

---

## 1. Activity Consistency Score
**Goal:** Reward steady, predictable content creation while penalizing erratic, "boom-and-bust" posting behavior. 

Instead of measuring raw volume, we measure the **Coefficient of Variation** across monthly buckets. We apply a Base-2 Logarithm to dampen massive viral spikes.

**Formula:**
$$S_{consistency} = \max\left(0, 100 \times \left(1 - \frac{\sigma}{\mu + \epsilon}\right)\right)$$

* **$\mu$ (Log-Mean):** Average of $\log_2(\text{posts} + 1)$ for each month.
* **$\sigma$ (Log-Deviation):** Standard deviation of those logarithmic values.
* **$\epsilon$ (Epsilon):** A floor value to prevent division by zero for inactive accounts.

---

## 2. Network Engagement Score
**Goal:** Measure true community interaction by weighing deep text engagement (comments/reposts) over shallow vanity metrics (likes). It also rewards reciprocity (giving recommendations).

**Formula:**
$$\text{Depth Ratio}_{post} = \frac{(\text{Comments} \times C_w) + (\text{Reposts} \times R_w)}{\text{Likes} + 1}$$

$$S_{engagement} = \min\left(100, (\text{Avg Depth Ratio} \times 100) + (\min(Rec_{given}, Rec_{received}) \times R_{bonus})\right)$$

---

## 3. Professional Depth Score
**Goal:** Balance structured career experience against community-validated skills. Skill endorsements face heavy logarithmic diminishing returns to prevent a single highly-endorsed skill from breaking the scale.

**Formula:**
$$S_{depth} = \min\left(100, (\text{Roles} \times \alpha) + (\text{Certs} \times \beta) + \left(\gamma \times \sum \log_2(\text{Endorsements}_i + 1)\right)\right)$$

---

## 4. Authority & Reach Score
**Goal:** Normalize massive audience sizes. The gap between 500 and 1,000 followers is mathematically more significant than the gap between 100,000 and 100,500.

**Formula:**
$$S_{authority} = \min\left(100, \lambda \times \log_{10}(\text{Followers} + \text{Connections} + 1)\right)$$

---

## 5. Profile Optimization Score
**Goal:** A straightforward percentage evaluating the utilization of native platform features.

**Formula:**
$$S_{optimization} = \left( \frac{F_{active}}{F_{target}} \right) \times 100$$
*(Target features: Custom URL, Banner Image, About Section, Featured Section, Education)*

---
---

## 🧪 Example Calculation Walkthrough

Let's evaluate a hypothetical candidate, **Jane Doe**, using the Default Persona constants.

### 📊 Jane's Raw Telemetry
* **Posts (Last 4 Months):** Month 1 (3 posts), Month 2 (7 posts), Month 3 (0 posts), Month 4 (1 post)
* **Recent Post Stats:** Post 1 (10 Likes, 2 Comments, 1 Repost). Post 2 (20 Likes, 5 Comments, 0 Reposts).
* **Recommendations:** Given (2), Received (3)
* **Experience Roles:** 3
* **Certifications:** 2
* **Skills:** Python (3 endorsements), Git (7 endorsements)
* **Audience:** 4,000 Followers, 500 Connections (Total: 4,500)
* **Optimization:** Has Banner, About, URL, Education. (Missing Featured). Active = 4.

---

### Step 1: Consistency
* **Log Values:** $\log_2(3+1)=2$, $\log_2(7+1)=3$, $\log_2(0+1)=0$, $\log_2(1+1)=1$.
* **$\mu$ (Mean):** $(2 + 3 + 0 + 1) / 4 = \mathbf{1.5}$
* **$\sigma^2$ (Variance):** $((2-1.5)^2 + (3-1.5)^2 + (0-1.5)^2 + (1-1.5)^2) / 4 = 1.25$
* **$\sigma$ (Deviation):** $\sqrt{1.25} \approx \mathbf{1.118}$
* **Calculation:** $100 \times \left(1 - \frac{1.118}{1.5 + 1.0}\right) = 100 \times (1 - 0.447)$
* **Consistency Score:** **55.30 / 100**

### Step 2: Engagement
* **Post 1 Depth:** $((2 \times 2.0) + (1 \times 1.5)) / 11 = 5.5 / 11 = \mathbf{0.50}$
* **Post 2 Depth:** $((5 \times 2.0) + (0 \times 1.5)) / 21 = 10 / 21 = \mathbf{0.476}$
* **Avg Depth:** $(0.50 + 0.476) / 2 = \mathbf{0.488}$
* **Reciprocity:** $\min(2, 3) \times 10.0 = 2 \times 10.0 = \mathbf{20.0}$
* **Calculation:** $(0.488 \times 100) + 20.0$
* **Engagement Score:** **68.80 / 100**

### Step 3: Professional Depth
* **Role Points:** $3 \times 4.0 = \mathbf{12.0}$
* **Cert Points:** $2 \times 2.0 = \mathbf{4.0}$
* **Skill Points:** $1.5 \times (\log_2(3+1) + \log_2(7+1)) = 1.5 \times (2 + 3) = \mathbf{7.5}$
* **Calculation:** $12.0 + 4.0 + 7.5$
* **Depth Score:** **23.50 / 100**

### Step 4: Authority & Reach
* **Audience:** $4,500$
* **Calculation:** $25.0 \times \log_{10}(4501) \approx 25.0 \times 3.653$
* **Authority Score:** **91.33 / 100**

### Step 5: Optimization
* **Active:** $4$
* **Calculation:** $(4 / 5) \times 100$
* **Optimization Score:** **80.00 / 100**

---

## 🏆 Final Weighted Engine Score

To get the final grade, we multiply each category score by its configured weight.

| Category | Score | Weight | Weighted Value |
| :--- | :--- | :--- | :--- |
| **Consistency** | 55.30 | 20% | `11.06` |
| **Engagement** | 68.80 | 25% | `17.20` |
| **Depth** | 23.50 | 25% | `5.88` |
| **Authority** | 91.33 | 20% | `18.27` |
| **Optimization** | 80.00 | 10% | `8.00` |
| **FINAL GRADE** | | | **60.41 / 100** |

*In this scenario, Jane Doe is an authoritative figure with a large audience and decent engagement, but her sporadic posting schedule and lack of listed roles/certifications bring her overall score down to a 60.*