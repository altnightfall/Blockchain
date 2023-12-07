<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="#">Bitko In</a>
        <button class="navbar-toggler" type="button" 
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent" 
            @click="visible=!visible"
            >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="navbar-collapse" :class="!visible?'collapse':''" id="navbarSupportedContent">
          <ul class="navbar-nav">
            <li class="nav-item">
                <router-link to="/" class="nav-link" @click="visible=!visible">Home</router-link>
            </li>
            <li class="nav-item">
                <router-link to="/about" class="nav-link" @click="visible=!visible">About</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <router-view/>
  </div>
</template>
<script>
export default {
  compatConfig: { MODE: 3 }
}
</script>