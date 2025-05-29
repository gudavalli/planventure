import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api'; // Assuming you have a configured api service

function AdminAssignRole() {
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState('');
  const { user } = useContext(AuthContext);

  useEffect(() => {
    if (user && user.role === 'admin') {
      api.get('/auth/admin/users/assign-role') // Match your backend route
        .then(response => {
          setUsers(response.data.users_awaiting_assignment || []);
        })
        .catch(error => {
          console.error('Error fetching users for role assignment:', error);
          setMessage('Failed to load users.');
        });
    }
  }, [user]);

  const handleAssignRole = (userId, newRole) => {
    if (!newRole) {
        setMessage('Please select a role.');
        return;
    }
    api.put(`/auth/admin/users/${userId}/assign-role`, { role: newRole }) // Match your backend route
      .then(response => {
        setMessage(`Role ${newRole} assigned to user ${userId} successfully.`);
        // Refresh list or update user in local state
        setUsers(users.filter(u => u.id !== userId));
      })
      .catch(error => {
        console.error('Error assigning role:', error);
        setMessage(`Failed to assign role to user ${userId}.`);
      });
  };

  if (!user || user.role !== 'admin') {
    return <p>You are not authorized to view this page.</p>;
  }

  return (
    <div>
      <h2>Admin Role Assignment</h2>
      {message && <p>{message}</p>}
      {users.length === 0 ? <p>No users awaiting role assignment.</p> : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Name</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.email}</td>
                <td>{u.first_name} {u.last_name}</td>
                <td>
                  <select onChange={(e) => handleAssignRole(u.id, e.target.value)}>
                    <option value="">Select Role</option>
                    <option value="talent_lead">Talent Lead</option>
                    <option value="candidate">Candidate</option>
                    {/* Add other roles as needed, perhaps dynamically from an API later */}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminAssignRole;
