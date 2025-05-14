import Navigation from '../components/Navigation';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      
      <main className="py-10">
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-semibold text-gray-900">
                Welcome, {user?.first_name || 'User'}!
              </h1>
              
              <div className="mt-6">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
                  <p className="text-gray-500">
                    Dashboard content will go here
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
