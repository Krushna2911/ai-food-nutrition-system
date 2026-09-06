import { useState } from 'react'
import './App.css'

function App() {
 const [selectedImage, setSelectedImage] = useState(null)
 const [analysisResult, setAnalysisResult] = useState(null)
 const [nutritionResult, setNutritionResult] = useState(null)
  return (
    <main className="app">
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

      <section id="analysis" className="analysis-section">
        <div className="section-heading">
          <p className="eyebrow">FOOD ANALYSIS</p>
          <h2>Start with a food image</h2>
          <p>
            Our analysis workflow will identify food items and connect them
            with nutrition information.
          </p>
        </div>

        <div className="upload-card">

         {analysisResult && nutritionResult && (
            <div className="analysis-result">
              <p className="eyebrow">ANALYSIS RESULT</p>

              <h3>{analysisResult.detections[0].class_name}</h3>

              <p>
                Confidence:{' '}
                {(analysisResult.detections[0].confidence * 100).toFixed(1)}%
              </p>

              <div className="nutrition-info">
                <p>Calories: {nutritionResult.calories} kcal</p>
                <p>Protein: {nutritionResult.protein_g} g</p>
                <p>Carbohydrates: {nutritionResult.carbohydrates_g} g</p>
                <p>Fat: {nutritionResult.fat_g} g</p>
              </div>
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
          <p>JPEG, PNG, or WEBP images are supported.</p>

          <label htmlFor="food-image" className="secondary-button">
            Choose Image
          </label>

          {selectedImage && (
            <button
              type="button"
              className="primary-button analysis-button"
              onClick={async () => {
                const input = document.getElementById('food-image')
                const file = input?.files?.[0]

                if (!file) {
                  return
                }

                const formData = new FormData()
                formData.append('file', file)

                const response = await fetch('http://localhost:8001/food/detect', {
                  method: 'POST',
                  body: formData,
                })

                const data = await response.json()
                setAnalysisResult(data)
                const nutritionResponse = await fetch(
                `http://localhost:8001/nutrition/${data.detections[0].class_name}`
              )

              const nutritionData = await nutritionResponse.json()

              console.log(nutritionData)
              setNutritionResult(nutritionData)
                console.log(data)
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
                setSelectedImage(URL.createObjectURL(file))
              }
            }}
          />
        </div>
      </section>

      <section id="diet" className="features-section">
        <div className="feature-card">
          <span>🔍</span>
          <h3>Food Detection</h3>
          <p>Identify food items from an uploaded image.</p>
        </div>

        <div className="feature-card">
          <span>🍎</span>
          <h3>Nutrition Estimation</h3>
          <p>Connect detected foods with nutrition information.</p>
        </div>

        <div className="feature-card">
          <span>📋</span>
          <h3>Personalized Diet</h3>
          <p>Build toward personalized dietary planning.</p>
        </div>
      </section>
    </main>
  )
}

export default App