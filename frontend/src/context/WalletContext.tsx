import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { api } from "../api/client";

type WalletType = "evm" | "solana";

interface WalletState {
  address: string | null;
  walletType: WalletType | null;
  connected: boolean;
  connecting: boolean;
  balance: string | null;
}

interface WalletContextType extends WalletState {
  connectEVM: () => Promise<void>;
  connectSolana: () => Promise<void>;
  disconnect: () => Promise<void>;
  linkToAccount: (email: string, password: string) => Promise<import("../types").AuthResponse>;
}

const WalletContext = createContext<WalletContextType | null>(null);

declare global {
  interface Window {
    ethereum?: {
      isMetaMask?: boolean;
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
      on: (event: string, handler: (...args: unknown[]) => void) => void;
      removeListener: (event: string, handler: (...args: unknown[]) => void) => void;
    };
    solana?: {
      isPhantom?: boolean;
      connect: () => Promise<{ publicKey: { toString: () => string } }>;
      disconnect: () => Promise<void>;
      signMessage: (message: Uint8Array) => Promise<{ signature: Uint8Array }>;
      on: (event: string, handler: (...args: unknown[]) => void) => void;
      removeListener: (event: string, handler: (...args: unknown[]) => void) => void;
    };
  }
}

function truncateAddress(addr: string): string {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

function base58Encode(bytes: Uint8Array): string {
  const ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  if (bytes.length === 0) return "";
  const digits = [0];
  for (let i = 0; i < bytes.length; i++) {
    let carry = bytes[i];
    for (let j = 0; j < digits.length; j++) {
      carry += digits[j] << 8;
      digits[j] = carry % 58;
      carry = (carry / 58) | 0;
    }
    while (carry > 0) {
      digits.push(carry % 58);
      carry = (carry / 58) | 0;
    }
  }
  let zeros = 0;
  while (zeros < bytes.length && bytes[zeros] === 0) zeros++;
  const result = [];
  for (let i = 0; i < zeros; i++) result.push("1");
  for (let i = digits.length - 1; i >= 0; i--) result.push(ALPHABET[digits[i]]);
  return result.join("");
}

export function WalletProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WalletState>({
    address: null,
    walletType: null,
    connected: false,
    connecting: false,
    balance: null,
  });

  useEffect(() => {
    const saved = localStorage.getItem("wallet_address");
    const savedType = localStorage.getItem("wallet_type") as WalletType | null;
    if (saved && savedType) {
      setState((s) => ({ ...s, address: saved, walletType: savedType, connected: true }));
    }
  }, []);

  const disconnect = useCallback(async () => {
    if (state.walletType === "solana" && window.solana) {
      try { await window.solana.disconnect(); } catch {}
    }
    localStorage.removeItem("wallet_address");
    localStorage.removeItem("wallet_type");
    setState({ address: null, walletType: null, connected: false, connecting: false, balance: null });
  }, [state.walletType]);

  const connectEVM = useCallback(async () => {
    if (!window.ethereum) {
      alert("Please install MetaMask or another EVM wallet");
      return;
    }
    setState((s) => ({ ...s, connecting: true }));
    try {
      const accounts = (await window.ethereum.request({ method: "eth_requestAccounts" })) as string[];
      const address = accounts[0].toLowerCase();

      const { message } = await api.walletNonce(address, "evm");
      const signature = (await window.ethereum.request({
        method: "personal_sign",
        params: [message, address],
      })) as string;

      await api.saveWallet({ address, signature, message, wallet_type: "evm" });

      localStorage.setItem("wallet_address", address);
      localStorage.setItem("wallet_type", "evm");
      setState({ address, walletType: "evm", connected: true, connecting: false, balance: null });
    } catch (err) {
      console.error("EVM connect error:", err);
      setState((s) => ({ ...s, connecting: false }));
    }
  }, []);

  const connectSolana = useCallback(async () => {
    if (!window.solana) {
      alert("Please install Phantom or another Solana wallet");
      return;
    }
    setState((s) => ({ ...s, connecting: true }));
    try {
      const { publicKey } = await window.solana.connect();
      const address = publicKey.toString();

      const { message } = await api.walletNonce(address, "solana");
      const encodedMsg = new TextEncoder().encode(message);
      const { signature } = await window.solana.signMessage(encodedMsg);
      const sigBase58 = base58Encode(signature);

      await api.saveWallet({ address, signature: sigBase58, message, wallet_type: "solana" });

      localStorage.setItem("wallet_address", address);
      localStorage.setItem("wallet_type", "solana");
      setState({ address, walletType: "solana", connected: true, connecting: false, balance: null });
    } catch (err) {
      console.error("Solana connect error:", err);
      setState((s) => ({ ...s, connecting: false }));
    }
  }, []);

  const linkToAccount = useCallback(async (email: string, password: string) => {
    if (!state.address || !state.walletType) throw new Error("Connect wallet first");
    const walletType = state.walletType;
    const address = state.address;

    const { message } = await api.walletNonce(address, walletType);

    let signature: string;
    if (walletType === "evm" && window.ethereum) {
      signature = (await window.ethereum.request({
        method: "personal_sign",
        params: [message, address],
      })) as string;
    } else if (walletType === "solana" && window.solana) {
      const encodedMsg = new TextEncoder().encode(message);
      const sig = await window.solana.signMessage(encodedMsg);
      signature = base58Encode(sig.signature);
    } else {
      throw new Error("Wallet not available");
    }

    const result = await api.walletLink(email, password, address, signature, message, walletType);
    return result;
  }, [state.address, state.walletType]);

  return (
    <WalletContext.Provider value={{ ...state, connectEVM, connectSolana, disconnect, linkToAccount }}>
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const ctx = useContext(WalletContext);
  if (!ctx) throw new Error("useWallet must be used within WalletProvider");
  return ctx;
}

export { truncateAddress };
