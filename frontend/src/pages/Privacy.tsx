import { motion } from "framer-motion";
import { PageTransition } from "../components/PageTransition";
import { AppNavbar } from "../components/Navbar";

const sections = [
  {
    title: "Information We Collect",
    content: "We collect information you provide during account registration, including your name, email address, and billing information. We also collect trading data such as signals generated, positions opened, and performance metrics to improve our algorithms. MEXC API keys are collected solely for trade execution and are never used for any other purpose. Usage data including page interactions and feature usage is collected anonymously to improve the platform."
  },
  {
    title: "How We Use Information",
    content: "Your information is used to operate and maintain the NexTrade AI platform, process subscriptions, generate trading signals, and provide customer support. We use trading data to optimize our 8 trading strategies and improve risk management systems. Aggregated, anonymized data may be used for research and product development. We never use your personal information for advertising or sell it to third parties."
  },
  {
    title: "Data Security",
    content: "All sensitive data, including MEXC API keys, is encrypted at rest using AES-256 encryption. Data in transit is protected using TLS 1.3. We employ industry-standard security practices including regular security audits, penetration testing, and access controls. Our infrastructure is hosted on secure cloud providers with physical security measures. Despite these measures, no method of electronic storage is 100% secure."
  },
  {
    title: "Third-Party Services",
    content: "NexTrade AI integrates with MEXC exchange for trade execution. Your data may be processed by our cloud infrastructure providers, payment processors, and monitoring services. Each third-party provider is vetted for security compliance and bound by data processing agreements. We do not share your API keys or trading strategies with any third party. MEXC receives only the trading instructions you authorize."
  },
  {
    title: "Cookies",
    content: "We use essential cookies for authentication and platform functionality. Analytics cookies help us understand usage patterns and improve performance. You can control cookie preferences through your browser settings. Disabling certain cookies may affect platform functionality. We do not use cookies for tracking across third-party websites."
  },
  {
    title: "Your Rights",
    content: "You have the right to access, correct, or delete your personal data at any time through your account settings. You may export your trading data in machine-readable format. You can request complete deletion of your account and associated data within 30 days of termination. To exercise these rights, contact support or use the account settings panel. We will respond to all legitimate requests within 30 days."
  },
  {
    title: "Contact",
    content: "For privacy-related inquiries, contact us at privacy@nextrade.ai or write to: NexTrade AI, Larnaca, Cyprus. Our Data Protection Officer can be reached at dpo@nextrade.ai. We will address any concerns or complaints regarding your privacy within 30 days."
  }
];

export default function Privacy() {
  return (
    <div className="min-h-screen bg-dark-950">
      <AppNavbar />
      <PageTransition>
        <div className="max-w-4xl mx-auto px-6 py-16">
          <div className="text-center mb-16">
            <h1 className="font-heading text-4xl md:text-5xl font-bold mb-4">Privacy Policy</h1>
            <p className="text-gray-400 text-sm">Last updated: June 1, 2026</p>
          </div>

          <div className="space-y-6">
            {sections.map((section) => (
              <motion.div key={section.title} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="bg-dark-800/40 border border-white/[0.06] rounded-2xl p-6">
                <h2 className="font-heading text-lg font-bold mb-3">{section.title}</h2>
                <p className="text-gray-400 text-sm leading-relaxed">{section.content}</p>
              </motion.div>
            ))}
          </div>

          <div className="mt-12 p-6 bg-dark-800/20 border border-white/[0.04] rounded-2xl">
            <p className="text-gray-500 text-xs leading-relaxed">
              NexTrade AI does not sell your personal data. All MEXC API keys are encrypted with AES-256 at rest and in transit. We are committed to protecting your privacy and maintaining your trust.
            </p>
          </div>
        </div>
      </PageTransition>
    </div>
  );
}
