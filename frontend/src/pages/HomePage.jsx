import HeroSection from '../components/HeroSection'
import FeatureCards from '../components/FeatureCards'
import PurpleBanner from '../components/PurpleBanner'
import TeamAbout from '../components/TeamAbout'

export default function HomePage() {
  return (
    <div className="home-page">
      <HeroSection />
      <FeatureCards />
      <PurpleBanner />
      <TeamAbout />
    </div>
  )
}
