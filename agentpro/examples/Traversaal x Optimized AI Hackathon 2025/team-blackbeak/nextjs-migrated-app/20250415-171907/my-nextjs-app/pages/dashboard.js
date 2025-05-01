import React from 'react';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

const Dashboard = ({ username }) => (
  <>
    <Header />
    <Navigation username={username} />
    <div className="content">
      This is Admin's Panel. You have entered in the backend zone.
    </div>
    <Footer />
  </>
);

export async function getServerSideProps({ req }) {
  const { username } = req.session;

  if (!username) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  return { props: { username } };
}

export default Dashboard;