<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const players = ref([])
const form = ref({ id: null, name: '', team: '' })
const editing = ref(false)

async function load() {
  const res = await api.get('/players')
  players.value = res.data
}

function edit(player: any) {
  form.value = { ...player }
  editing.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/players/${form.value.id}`, form.value)
  } else {
    await api.post(`/players`, form.value)
  }

  form.value = { id: null, name: '', team: '' }
  editing.value = false

  load()
}

async function remove(id: number) {
  await api.delete(`/players/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-content">
    <h1>Manage Players</h1>

    <form class="edit-form fx-glow">
      <input v-model="form.name" placeholder="Name" />
      <input v-model="form.team" placeholder="Team" />
      <button class="ww-btn" @click.prevent="save">
        {{ editing ? 'Update' : 'Create' }}
      </button>
    </form>

    <table class="table">
      <thead><tr><th>Name</th><th>Team</th><th></th></tr></thead>
      <tbody>
        <tr v-for="p in players" :key="p.id">
          <td>{{ p.name }}</td>
          <td>{{ p.team }}</td>
          <td>
            <button @click="edit(p)">Edit</button>
            <button @click="remove(p.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

