import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDa7pEn1hUn2iBrlgMaYq4bDgYMP5UygDg",
  authDomain: "ehc-c-buskey-506b97.firebaseapp.com",
  projectId: "ehc-c-buskey-506b97",
  storageBucket: "ehc-c-buskey-506b97.firebasestorage.app",
  messagingSenderId: "1044218128888",
  appId: "1:1044218128888:web:55f33df7776786a1e88e0d",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

const provider = new GoogleAuthProvider();
provider.setCustomParameters({ hd: "salesforce.com" }); // restrict to @salesforce.com

export async function signInWithGoogle() {
  await signInWithPopup(auth, provider);
}

export async function signOutUser() {
  await signOut(auth);
}
