import Link from 'next/link';
import { Home, BrainCircuit, Map, ListTodo, MessageSquare, Compass, Clock, BookOpen } from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Learning History', href: '/history', icon: Clock },
    { name: 'Mistake Analyzer', href: '/analyzer', icon: BrainCircuit },
    { name: 'Knowledge Map', href: '/knowledge', icon: Map },
    { name: 'Practice Quiz', href: '/quiz', icon: ListTodo },
    { name: 'Teach-Back', href: '/teachback', icon: MessageSquare },
    { name: 'Recommendations', href: '/recommendations', icon: Compass },
    { name: 'Curriculum', href: '/curriculum', icon: BookOpen },
  ];

  return (
    <div className="flex flex-col w-64 bg-slate-900 h-screen text-slate-300">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <BrainCircuit className="text-blue-500" />
          AI Study
        </h1>
        <p className="text-xs text-slate-500 mt-1">Intelligent Learning</p>
      </div>
      
      <nav className="flex-1 px-4 mt-6 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link 
              key={item.name} 
              href={item.href}
              className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
            >
              <Icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
            S
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-white">Student User</span>
            <span className="text-xs text-slate-500">ID: student_1</span>
          </div>
        </div>
      </div>
    </div>
  );
}
