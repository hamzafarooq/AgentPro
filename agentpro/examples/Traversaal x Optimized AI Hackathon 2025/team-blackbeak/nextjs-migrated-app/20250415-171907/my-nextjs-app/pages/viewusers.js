import React from 'react';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

const ViewUsers = ({ users, username }) => (
  <>
    <Header />
    <Navigation username={username} />
    <div className="content">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Gender</th>
            <th>Username</th>
            <th>Password</th>
            <th>Address</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td>
              <td>{user.gender}</td>
              <td>{user.username}</td>
              <td>{user.password}</td>
              <td>{user.address}</td>
              <td>{user.email}</td>
              <td><a href={`/updateusers?id=${user.id}`}>Update</a></td>
              <td><a href={`/deleteusers?id=${user.id}`}>Delete</a></td>
            </tr>
          ))}
        </tbody>
      </table>
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

  const res = await fetch('http://localhost:3000/api/viewusers');
  const users = await res.json();

  return { props: { users, username } };
}

export default ViewUsers;