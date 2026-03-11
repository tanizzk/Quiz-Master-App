document.addEventListener("DOMContentLoaded", () => {

  const cards = Array.from(document.querySelectorAll(".quiz-question"))

  if (!cards.length) return

  const prevBtn = document.getElementById("prev-question")
  const nextBtn = document.getElementById("next-question")
  const counter = document.getElementById("question-counter")
  const progressBar = document.getElementById("progress-bar")

  const submitBtn = document.getElementById("quiz-submit")
  const confirmBtn = document.getElementById("confirm-submit")
  const quizForm = document.getElementById("quiz-form")

  let activeIndex = 0
  const total = cards.length

  const showCard = (index) => {

    cards.forEach((card,i) => {

      if(i === index){
        card.classList.add("active")
      } else {
        card.classList.remove("active")
      }

    })

    if(counter){
      counter.textContent = "Question " + (index+1) + "/" + total
    }

    if(progressBar){

      const percent = Math.round(((index+1)/total)*100)

      progressBar.style.width = percent + "%"
      progressBar.setAttribute("aria-valuenow", percent)

    }

    if(prevBtn) prevBtn.disabled = index === 0
    if(nextBtn) nextBtn.disabled = index === total-1

  }

  if(prevBtn){
    prevBtn.addEventListener("click",()=>{

      if(activeIndex > 0){
        activeIndex -= 1
        showCard(activeIndex)
      }

    })
  }

  if(nextBtn){
    nextBtn.addEventListener("click",()=>{

      if(activeIndex < total-1){
        activeIndex += 1
        showCard(activeIndex)
      }

    })
  }

  showCard(activeIndex)

  if(submitBtn){

    submitBtn.addEventListener("click",(e)=>{

      e.preventDefault()

      const modal = new bootstrap.Modal(
        document.getElementById("submitModal")
      )

      modal.show()

    })

  }

  if(confirmBtn){

    confirmBtn.addEventListener("click",()=>{

      if(quizForm) quizForm.submit()

    })

  }

})