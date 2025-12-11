<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const resonators = ref([])
const form = ref({ id: null, name: '', type: '', power: 0 })
const editing = ref(false)

async function load() {
  const res = await api.get('/resonators')
  resonators.value = res.data
}

function edit(resonator: any) {
  form.value = { ...resonator }
  editing.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/resonators/${form.value.id}`, form.value)
  } else {
    await api.post('/resonators', form.value)
  }
  form.value = { id: null, name: '', type: '', power: 0 }
  editing.value = false
  load()
}

async function remove(id: number) {
  await api.delete(`/resonators/${id}`)
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-content">
    <h1>Manage Resonators</h1>

    <form class="edit-form fx-glow">
      <input v-model="form.name" placeholder="Name" />
      <input v-model="form.type" placeholder="Type" />
      <input v-model.number="form.power" type="number" placeholder="Power" />
      <button class="ww-btn" @click.prevent="save">{{ editing ? 'Update' : 'Create' }}</button>
    </form>

    <table class="table">
      <thead>
        <tr><th>Name</th><th>Type</th><th>Power</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="r in resonators" :key="r.id">
          <td>{{ r.name }}</td>
          <td>{{ r.type }}</td>
          <td>{{ r.power }}</td>
          <td>
            <button @click="edit(r)">Edit</button>
            <button @click="remove(r.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

