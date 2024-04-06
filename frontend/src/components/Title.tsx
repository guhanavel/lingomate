import { useState } from "react";



type Props = {
  setMessages: any;
  setFeedback: any;
  setSuggested: any;

};


  // create function called createBlobUrl to convert any audio to Blob
  function createBlobURL(data: any) {
    const blob = new Blob([data], { type: "audio/mpeg" });
    const url = window.URL.createObjectURL(blob);
    return url;
  }

function Title({  setMessages, setFeedback, setSuggested }: Props) {
  const [isResetting, setIsResetting] = useState(false);
  const [, setClickCount] = useState(0);


  // Reset conversation
  const resetConversation = async () => {
    setIsResetting(true);
    setClickCount(0);

    try {

      const response_text = await fetch('http://localhost:8000/reset-text');
      const response_audio = await fetch('http://localhost:8000/reset-voice');
      const data = await response_text.json();
      const blob = await response_audio.blob();
      const audio = new Audio();
      audio.src = createBlobURL(blob);
      setMessages([{ sender: "Edubot", blobUrl: audio.src, text: data }]);
      setFeedback([])
      setSuggested([])

      audio.play();
    } catch (error) {
      console.error('Error fetching data:', error);
    }

    setIsResetting(false);
  };



  return (
    <div className="flex justify-between items-center w-full p-4 bg-gray-900 text-white font-bold shadow">
      <div className="italic">Lingomate</div>
      <button
        onClick={resetConversation}
        className={
          "transition-all duration-300 text-blue-300 hover:text-pink-500 " +
          (isResetting && "animate-pulse")
        }
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
          />
        </svg>
        
      </button>

    </div>
  );
}

export default Title;
