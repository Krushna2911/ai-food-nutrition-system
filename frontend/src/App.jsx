import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [segmentationResult, setSegmentationResult] = useState(null)
  const imageRef = useRef(null)
      const [imageDimensions, setImageDimensions] = useState({
        width: 0,
        height: 0,
      })
  const [nutritionResult, setNutritionResult] = useState(null)
  const [analysisHistory, setAnalysisHistory] = useState([])
  const [showAllHistory, setShowAllHistory] = useState(false)
  const [selectedHistory, setSelectedHistory] = useState(null)

  const [profileSaved, setProfileSaved] = useState(false)

  const [portionSize, setPortionSize] = useState('')
  const [selectedFood, setSelectedFood] = useState('')

  const [profile, setProfile] = useState({
    age: '',
    height_cm: '',
    weight_kg: '',
    activity_level: 'moderate',
    diet_goal: 'maintenance',
    dietary_preference: 'balanced',
    food_restrictions: '',
  })

  const [nutritionRequirements, setNutritionRequirements] = useState(null)

  const [dietPlan, setDietPlan] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [dietPlanLoading, setDietPlanLoading] = useState(false)

  const generateDietPlan = async () => {
  const profileId = localStorage.getItem('profileId')

      if (!profileId) {
        alert('Please save your profile first.')
        return
      }

      setDietPlanLoading(true)

      try {
        const response = await fetch('http://localhost:8000/diet-plan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            profile_id: Number(profileId),
          }),
        })

        const data = await response.json()

        if (!response.ok) {
          console.error('Diet plan generation failed:', data)
          alert(data.detail || 'Failed to generate diet plan.')
          return
        }

        setDietPlan(data)
          const recommendationResponse = await fetch('http://127.0.0.1:8000/recommendation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ profile_id: profileId }),
        })

        if (!recommendationResponse.ok) {
          throw new Error('Failed to generate recommendation')
        }

        const recommendationData = await recommendationResponse.json()
        setRecommendation(recommendationData)


      } catch (error) {
        console.error('Diet plan error:', error)
        alert('Unable to generate diet plan.')
      } finally {
        setDietPlanLoading(false)
      }
    }

  // Load a saved profile from the backend


  // Load analysis history when the page opens
  useEffect(() => {
    fetch('http://localhost:8000/analysis')
      .then((response) => response.json())
      .then((data) => {
        setAnalysisHistory(data)

      })
      .catch((error) => {
        console.error('Analysis history error:', error)
      })
  }, [])

  // Load saved profile when the page opens
 useEffect(() => {
  const savedProfileId = localStorage.getItem('profileId')

  if (!savedProfileId) {
    return
  }

  fetch(`http://localhost:8000/profile/${savedProfileId}`)
    .then((response) => response.json())
    .then((data) => {
      setProfile({
        age: data.age,
        height_cm: data.height_cm,
        weight_kg: data.weight_kg,
        activity_level: data.activity_level,
        diet_goal: data.diet_goal,
        dietary_preference: data.dietary_preference,
        food_restrictions: data.food_restrictions || '',
      })

      setProfileSaved(true)


    })

    .catch((error) => {
      console.error('Profile load error:', error)
    })
}, [])
  // Save profile to the backend
  const saveProfile = async () => {
    if (!profile.age || !profile.height_cm || !profile.weight_kg) {
      alert('Please enter age, height, and weight.')
      return
}
    if (
      Number(profile.age) <= 0 ||
      Number(profile.height_cm) <= 0 ||
      Number(profile.weight_kg) <= 0
    ) {
      alert('Age, height, and weight must be greater than zero.')
      return
  }

  if (Number(profile.age) < 13 || Number(profile.age) > 120) {
  alert('Please enter an age between 13 and 120.')
  return
}

 if (Number(profile.height_cm) < 50 || Number(profile.height_cm) > 250) {
  alert('Please enter a height between 50 and 250 cm.')
  return
}

if (Number(profile.weight_kg) < 20 || Number(profile.weight_kg) > 300) {
  alert('Please enter a weight between 20 and 300 kg.')
  return
}
    try {
      const response = await fetch('http://localhost:8000/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: Number(profile.age),
          height_cm: Number(profile.height_cm),
          weight_kg: Number(profile.weight_kg),
          activity_level: profile.activity_level,
          diet_goal: profile.diet_goal,
          dietary_preference: profile.dietary_preference,
          food_restrictions: profile.food_restrictions || null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        console.error('Profile save failed:', data)
        return
      }


      localStorage.setItem('profileId', data.id)
      setProfileSaved(true)


      const requirementResponse = await fetch(
  'http://localhost:8000/nutrition-requirements',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      age: Number(profile.age),
      height_cm: Number(profile.height_cm),
      weight_kg: Number(profile.weight_kg),
      activity_level: profile.activity_level,
      diet_goal: profile.diet_goal,
    }),
  }
)

const requirementData = await requirementResponse.json()

if (!requirementResponse.ok) {
  console.error(
    'Nutrition requirement calculation failed:',
    requirementData
  )
  return
}

setNutritionRequirements(requirementData)



    } catch (error) {
      console.error('Profile save error:', error)
    }
  }

  return (
    <main className="app">

      {/* Navbar */}
      <header className="navbar">
        <div className="brand">
          <span className="brand-icon">&#x1F957;</span>
          <span>NutriVision AI</span>
        </div>

        <nav>
          <a href="#home">Home</a>
          <a href="#analysis">Food Analysis</a>
          <a href="#diet">Diet Plan</a>
        </nav>
      </header>

      {/* Hero */}
      <section id="home" className="hero-section">
        <div className="hero-content">
          <p className="eyebrow">AI-POWERED NUTRITION</p>

          <h1>
            Understand your food.
            <br />
            Improve your nutrition.
          </h1>

          <p className="hero-description">
            Upload a food image and get food detection, nutrition
            information, and personalized dietary guidance.
          </p>

          <a href="#analysis" className="primary-button">
            Analyze Food
          </a>
        </div>
      </section>

      {/* User Profile */}
      <section id="profile" className="profile-section">
        <div className="section-heading">
          <p className="eyebrow">USER PROFILE</p>

          <h2>Personalize your nutrition plan</h2>

          <p>
            Enter your details to help us create personalized
            recommendations.
          </p>
        </div>

        <div className="profile-form">

          <label>
            Age
            <input
              type="number"
              value={profile.age}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  age: event.target.value,
                })
              }
              placeholder="Enter your age"
            />
          </label>

          <label>
            Height (cm)
            <input
              type="number"
              value={profile.height_cm}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  height_cm: event.target.value,
                })
              }
              placeholder="Enter your height"
            />
          </label>

          <label>
            Weight (kg)
            <input
              type="number"
              value={profile.weight_kg}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  weight_kg: event.target.value,
                })
              }
              placeholder="Enter your weight"
            />
          </label>

          <label>
            Activity level
            <select
              value={profile.activity_level}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  activity_level: event.target.value,
                })
              }
            >
              <option value="sedentary">Sedentary</option>
              <option value="light">Light</option>
              <option value="moderate">Moderate</option>
              <option value="active">Active</option>
              <option value="very_active">Very active</option>
            </select>
          </label>

          <label>
            Diet goal
            <select
              value={profile.diet_goal}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  diet_goal: event.target.value,
                })
              }
            >
              <option value="weight_loss">Weight loss</option>
              <option value="maintenance">Maintenance</option>
              <option value="weight_gain">Weight gain</option>
            </select>
          </label>

          <label>
            Dietary preference
            <select
              value={profile.dietary_preference}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  dietary_preference: event.target.value,
                })
              }
            >
              <option value="balanced">Balanced</option>
              <option value="vegetarian">Vegetarian</option>
              <option value="vegan">Vegan</option>
              <option value="non_vegetarian">
                Non-vegetarian
              </option>
            </select>
          </label>

          <label>
            Food restrictions / allergies
            <textarea
              value={profile.food_restrictions}
              onChange={(event) =>
                setProfile({
                  ...profile,
                  food_restrictions: event.target.value,
                })
              }
              placeholder="Example: peanuts, lactose"
              rows="3"
            />
          </label>

          <button
            type="button"
            className="primary-button profile-button"
            onClick={saveProfile}
          >
            Save Profile
          </button>

          {profileSaved && (
            <p className="profile-success">
              Profile saved successfully.
            </p>
          )}

          {nutritionRequirements && (
              <div className="nutrition-requirements">
                <p>
                  Daily calorie target:{' '}
                  <strong>{nutritionRequirements.daily_calories} kcal</strong>
                </p>

                <p>
                  Estimated BMR:{' '}
                  <strong>{nutritionRequirements.bmr} kcal</strong>
                </p>
              </div>
            )}

        </div>
      </section>

<section id="diet" className="features-section">
  <div className="section-heading">
    <p className="eyebrow">PERSONALIZED DIET PLAN</p>

    <h2>Your daily meal plan</h2>

    <p>
      Generate a calorie-targeted meal plan based on your saved profile.
    </p>

    <button
      type="button"
      className="primary-button"
      onClick={generateDietPlan}
      disabled={dietPlanLoading}
    >
      {dietPlanLoading ? 'Generating Plan...' : 'Generate Diet Plan'}
    </button>
  </div>

  {dietPlan && (
    <div className="diet-plan">
      <h3>
        Daily Target: {dietPlan.daily_calorie_target} kcal
      </h3>


       <div className="feature-card nutrition-summary-card">
         <h3>Daily Nutrition Summary</h3>


        <p>
          Total Calories: {dietPlan.total_calories} kcal
        </p>

        <p>
          Protein: {dietPlan.protein_g} g
        </p>

        <p>
          Carbohydrates: {dietPlan.carbohydrates_g} g
        </p>

        <p>
          Fat: {dietPlan.fat_g} g
        </p>

        <p>
          AMDR Compliant: {dietPlan.amdr_compliant ? 'Yes' : 'No'}
        </p>
      </div>

  {recommendation && (
    <div className="feature-card">
      <h3>AI Nutrition Guidance</h3>

        <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {recommendation.recommendation}
      </ReactMarkdown>
    </div>
  )}

      {dietPlan.meals.map((meal) => (
        <div className="feature-card" key={meal.meal}>
          <h3>{meal.meal}</h3>

          <p>
            Calories: {meal.calories} kcal
          </p>

          <p>
            Protein: {meal.protein_g} g
          </p>

          <p>
            Carbohydrates: {meal.carbohydrates_g} g
          </p>

          <p>
            Fat: {meal.fat_g} g
          </p>

          {meal.foods.map((food, index) => (
            <p key={index}>
              {food.food_name} â€” {food.portion_g} g
            </p>
          ))}
        </div>
      ))}
    </div>
  )}
</section>

      {/* Food Analysis */}
      <section id="analysis" className="analysis-section">
        <div className="section-heading">
          <p className="eyebrow">FOOD ANALYSIS</p>

          <h2>Start with a food image</h2>

          <p>
            Our analysis workflow will identify food items and
            connect them with nutrition information.
          </p>
        </div>

        <div className="upload-card">

      <div className="portion-input">
          <label htmlFor="portion-size">Portion size (g)</label>
          <input
            id="portion-size"
            type="number"
            min="1"
            placeholder="Enter portion size"
            value={portionSize}
            onChange={(event) => setPortionSize(event.target.value)}
          />
          </div>

          {segmentationResult &&
            segmentationResult.segmentations.length > 0 && (
              <div className="analysis-result">
                <p className="eyebrow">SEGMENTATION RESULT</p>

                {segmentationResult.segmentations.map((segment, index) => (
                  <div key={index}>
                    <h3>{segment.class_name}</h3>

                    <p>
                      Confidence:{' '}
                      {(segment.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                ))}
              </div>
            )}


          {analysisResult && analysisResult.detections.length > 0 && (
            <div className="analysis-result">
              <p className="eyebrow">ANALYSIS RESULT</p>

             {analysisResult.detections.map((detection, index) => (
                    <button
                      key={index}
                      type="button"
                      className="secondary-button"
                      onClick={() => {
                        setSelectedFood(detection.class_name)
                        setNutritionResult(null)
                      }}
                    >
                      {detection.class_name} (
                      {(detection.confidence * 100).toFixed(1)}%
                      )
                    </button>
                  ))}

                      {selectedFood && (
                        <p>
                          Selected food: <strong>{selectedFood}</strong>
                        </p>
                      )}

                    {selectedFood && (
              <button
                type="button"
                className="primary-button"
                onClick={async () => {

                  const nutritionResponse = await fetch(
                    'http://localhost:8000/nutrition/calculate',
                    {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        food_name: selectedFood,
                        portion_g: Number(portionSize),
                      }),
                    }
                  )

                  const nutritionData = await nutritionResponse.json()

                  if (nutritionResponse.ok) {
                    setNutritionResult(nutritionData)
                  } else {
                    setNutritionResult(null)
                    console.warn(
                      'Nutrition data unavailable:',
                      nutritionData.detail
                    )
                  }
                }}
              >
                Calculate Nutrition
              </button>
            )}


           {nutritionResult && (
                <div className="nutrition-info">
                <p>Portion: {nutritionResult.portion_g} g</p>

                <p>
                  Calories: {nutritionResult.calories} kcal
                </p>

                <p>
                  Protein: {nutritionResult.protein_g} g
                </p>

                <p>
                  Carbohydrates:{' '}
                  {nutritionResult.carbohydrates_g} g
                </p>

                <p>
                  Fat: {nutritionResult.fat_g} g
                </p>
              </div>
              )}
          </div>
          )}
        {selectedImage ? (
              <div
                style={{
                  position: 'relative',
                  display: 'inline-block',
                }}
              >
                <img
                  ref={imageRef}
                  src={selectedImage}
                  alt="Selected food"
                  className="image-preview"
                  onLoad={(event) => {
                    setImageDimensions({
                      width: event.target.naturalWidth,
                      height: event.target.naturalHeight,
                    })
                  }}
                />

                {segmentationResult &&
                  imageDimensions.width > 0 &&
                  imageDimensions.height > 0 && (
                    <svg
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    pointerEvents: 'none',
                  }}
                  viewBox={`0 0 ${imageDimensions.width} ${imageDimensions.height}`}
                  preserveAspectRatio="none"
                >
                  {segmentationResult.segmentations.map((segment, index) => {
                    const firstPoint = segment.polygon?.[0]

                    return (
                      <g key={index}>
                        <polygon
                          points={segment.polygon
                            .map(([x, y]) => `${x},${y}`)
                            .join(' ')}
                          fill="rgba(255, 165, 0, 0.25)"
                          stroke="orange"
                          strokeWidth="3"
                        />

                        {firstPoint && (
                          <text
                            x={firstPoint[0]}
                            y={firstPoint[1] - 5}
                            fill="orange"
                            fontSize="24"
                            fontWeight="bold"
                          >
                            {segment.class_name}
                          </text>
                        )}
                      </g>
                    )
                  })}
                </svg>
                  )}
              </div>
            ) : (
              <div className="upload-icon">&#x1F4F7;</div>
            )}

          <h3>Upload a food image</h3>

          <p>
            JPEG, PNG, or WEBP images are supported.
          </p>

          <label
            htmlFor="food-image"
            className="secondary-button"
          >
            Choose Image
          </label>

          {selectedImage && (
            <button
              type="button"
              className="primary-button analysis-button"
              onClick={async () => {

                const input =
                  document.getElementById('food-image')

                const file = input?.files?.[0]

                if (!file) {
                  return
                }

                const formData = new FormData()
                formData.append('file', file)

                const response = await fetch(
                  'http://localhost:8000/food/detect',
                  {
                    method: 'POST',
                    body: formData,
                  }
                )

                const data = await response.json()

                setAnalysisResult(data)

                const segmentationFormData = new FormData()
                  segmentationFormData.append('file', file)

                  const segmentationResponse = await fetch(
                    'http://localhost:8000/food/segment',
                    {
                      method: 'POST',
                      body: segmentationFormData,
                    }
                  )

                  const segmentationData = await segmentationResponse.json()

                  if (segmentationResponse.ok) {
                    setSegmentationResult(segmentationData)

                  } else {
                    setSegmentationResult(null)
                    console.warn(
                      'Segmentation failed:',
                      segmentationData.detail
                    )
                  }


              }}
            >
              Analyze Image
            </button>
          )}

          <input
            id="food-image"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            hidden
            onChange={(event) => {
              const file = event.target.files?.[0]

              if (file) {
                  setSelectedFood('')
                  setNutritionResult(null)
                  setAnalysisResult(null)
                  setSegmentationResult(null)
                  setSelectedImage(
                  URL.createObjectURL(file)
                )
              }
            }}
          />

        </div>
      </section>

      {/* Analysis History */}
      <section id="history" className="history-section">
        <div className="section-heading">
          <p className="eyebrow">ANALYSIS HISTORY</p>

          <h2>Previous analyses</h2>

          <p>Your recent food analysis records.</p>
        </div>

        <div className="history-list">
          {analysisHistory
            .slice(0, showAllHistory ? analysisHistory.length : 5)
            .map((analysis) => (
            <div
              className="history-card"
              key={analysis.id}
              onClick={async () => {
                const response = await fetch(
                  `http://localhost:8000/analysis/${analysis.image_id}`
                )

                const data = await response.json()

                setSelectedHistory(data)


              }}
            >
              <span>&#x1F37D;&#xFE0F;</span>

              <div>
                <h3>Analysis #{analysis.id}</h3>

                <p>{analysis.image_id}</p>
              </div>
            </div>
          ))}
        </div>
        {analysisHistory.length > 5 && (
          <button
            type="button"
            className="secondary-button history-toggle"
            onClick={() => setShowAllHistory((current) => !current)}
          >
            {showAllHistory ? 'Show Less' : 'View All Analyses'}
          </button>
        )}
        {selectedHistory && (
          <div className="analysis-result">
            <p className="eyebrow">
              SELECTED ANALYSIS
            </p>

            <h3>
              {selectedHistory.detections[0].class_name}
            </h3>

            <p>
              Confidence:{' '}
              {(
                selectedHistory.detections[0].confidence *
                100
              ).toFixed(1)}
              %
            </p>
          </div>
        )}
      </section>

    </main>
  )
}

export default App
