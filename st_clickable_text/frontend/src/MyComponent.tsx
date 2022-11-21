import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"
import React, { useState, useCallback } from "react"

/**
 * This is a React-based component template with functional component and hooks.
 */
const MyComponent: React.VFC = () => {
  // "useRenderData" returns the renderData passed from Python.
  const renderData = useRenderData()

  const [currentWordIndex, setCurrentWordIndex] = useState(-1)

  /** Click handler for our "Click Me!" button. */
  const setWord = useCallback((index) => {
    setCurrentWordIndex(index)
    Streamlit.setComponentValue(index)
  }, [])


  // Arguments that are passed to the plugin in Python are accessible
  // via `renderData.args`. Here, we access the "name" arg.
  const text: Array<string> = renderData.args["text"]

  // Show a button and some text.
  // When the button is clicked, we'll increment our "numClicks" state
  // variable, and send its new value back to Streamlit, where it'll
  // be available to the Python program.
  return (
    <span>
      {text.map((object, index) =>{
        if (index !== currentWordIndex) {
          return <span onClick={() => setWord(index)}>{object} </span>;
        } else
        {
          return <span onClick={() => setWord(index)}><b>{object}</b> </span>;
        }
      })}
    </span>
  )
}

export default MyComponent
