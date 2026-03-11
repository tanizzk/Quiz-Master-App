document.addEventListener("DOMContentLoaded", () => {

  const timer = document.getElementById("quiz-timer")

  if (!timer) return

  const duration = parseInt(timer.dataset.duration)

  if (!duration || duration <= 0) return

  let secondsLeft = duration * 60

  const format = (value) => {
    const minutes = Math.floor(value / 60)
    const seconds = value % 60

    return String(minutes).padStart(2,"0") + ":" + String(seconds).padStart(2,"0")
  }

  timer.textContent = format(secondsLeft)

  const interval = setInterval(() => {

    secondsLeft -= 1

    if (secondsLeft < 0) {
      clearInterval(interval)
      timer.textContent = "Time's up"

      const form = document.getElementById("quiz-form")

      if (form) form.submit()

      return
    }

    timer.textContent = format(secondsLeft)

  },1000)

})