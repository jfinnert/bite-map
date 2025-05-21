import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import SplitView from '../components/SplitView'
import '../styles/HomePage.css'

const HomePage = () => {
  return (
    <div className="home-page">
      <header className="app-header">
        <h1>Bite Map</h1>
        <p>Organize food videos by location</p>
      </header>
      
      <main className="app-content">
        <SplitView />
      </main>
      
      <ReactQueryDevtools initialIsOpen={false} />
    </div>
  )
}

export default HomePage
