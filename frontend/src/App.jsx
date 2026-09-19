import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [nutritionResult, setNutritionResult] = useState(null)
  const [analysisHistory, setAnalysisHistory] = useState([])
  const [selectedHistory, setSelectedHistory] = useState(null)

  const [profileSaved, setProfileSaved] = useState(false)

  const [portionSize, setPortionSize] = useState('')

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

  // Load a saved profile from the backend


  // Load analysis history when the page opens
  useEffect(() => {
    fetch('http://localhost:8001/analysis')
      .then((response) => response.json())
      .then((data) => {
        setAnalysisHistory(data)
        console.log('analysisHistory', data)
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

  fetch(`http://localhost:8001/profile/${savedProfileId}`)
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
      console.log('profile loaded', data)
      
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
      const response = await fetch('http://localhost:8001/profile', {
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
      console.log('SAVED PROFILE ID:', data.id)

      const requirementResponse = await fetch(
  'http://localhost:8001/nutrition-requirements',
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

console.log(
  'NUTRITION REQUIREMENTS:',
  requirementData
)

    } catch (error) {
      console.error('Profile save error:', error)
    }
  }

  return (
    <main className="app">

      {/* Navbar */}
      <header className="navbar">
        <div className="brand">
          <span className="brand-icon">🥗</span>
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

          {analysisResult && analysisResult.detections.length > 0 && (
            <div className="analysis-result">
              <p className="eyebrow">ANALYSIS RESULT</p>

              <h3>
                {analysisResult.detections[0].class_name}
              </h3>

              <p>
                Confidence:{' '}
                {(
                  analysisResult.detections[0].confidence * 100
                ).toFixed(1)}
                %
              </p>

              {analysisResult && analysisResult.detections.length > 0 && (
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
            <img
              src={selectedImage}
              alt="Selected food"
              className="image-preview"
            />
          ) : (
            <div className="upload-icon">📷</div>
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
                  'http://localhost:8001/food/detect',
                  {
                    method: 'POST',
                    body: formData,
                  }
                )

                const data = await response.json()

                setAnalysisResult(data)

                const nutritionResponse = await fetch(
                    'http://localhost:8001/nutrition/calculate',
                    {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        food_name: data.detections[0].class_name,
                        portion_g: Number(portionSize),
                      }),
                    }
)

                const nutritionData =
                  await nutritionResponse.json()

                if (nutritionResponse.ok) {
                  setNutritionResult(nutritionData)
                } else {
                  setNutritionResult(null)
                  console.warn(
                    'Nutrition data unavailable:',
                    nutritionData.detail
                  )
                }

                console.log('analysis result', data)
                console.log(
                  'nutrition result',
                  nutritionData
                )
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
          {analysisHistory.map((analysis) => (
            <div
              className="history-card"
              key={analysis.id}
              onClick={async () => {
                const response = await fetch(
                  `http://localhost:8001/analysis/${analysis.image_id}`
                )

                const data = await response.json()

                setSelectedHistory(data)

                console.log('historyDetail', data)
              }}
            >
              <span>🍽️</span>

              <div>
                <h3>Analysis #{analysis.id}</h3>

                <p>{analysis.image_id}</p>
              </div>
            </div>
          ))}
        </div>

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

      {/* Features */}
      <section id="diet" className="features-section">

        <div className="feature-card">
          <span>🔍</span>

          <h3>Food Detection</h3>

          <p>
            Identify food items from an uploaded image.
          </p>
        </div>

        <div className="feature-card">
          <span>🍎</span>

          <h3>Nutrition Estimation</h3>

          <p>
            Connect detected foods with nutrition information.
          </p>
        </div>

        <div className="feature-card">
          <span>📋</span>

          <h3>Personalized Diet</h3>

          <p>
            Build toward personalized dietary planning.
          </p>
        </div>

      </section>

    </main>
  )
}

export default App